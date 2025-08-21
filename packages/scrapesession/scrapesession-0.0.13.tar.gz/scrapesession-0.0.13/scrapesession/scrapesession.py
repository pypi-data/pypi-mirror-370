"""A session for efficient scraping."""

# pylint: disable=too-many-positional-arguments,abstract-method,protected-access,too-many-arguments,too-many-instance-attributes,bare-except
import datetime
import http
import logging
import os
import random
import re
import sqlite3
import urllib.parse
from contextlib import contextmanager
from io import BytesIO
from typing import Any, MutableMapping, Optional

import numpy as np
import requests
import requests_cache
import urllib3
import wayback  # type: ignore
from func_timeout import FunctionTimedOut, func_set_timeout  # type: ignore
from playwright.sync_api import sync_playwright
from random_user_agent.params import OperatingSystem  # type: ignore
from random_user_agent.params import SoftwareName
from random_user_agent.user_agent import UserAgent  # type: ignore
from requests import PreparedRequest
from requests.cookies import RequestsCookieJar
from requests.models import Request, Response
from requests.structures import CaseInsensitiveDict
from requests_cache import AnyResponse, ExpirationTime
from tenacity import (after_log, before_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_random_exponential)
from urllib3.response import HTTPResponse

from .cookie_policy import BlockAll
from .playwright import ensure_install
from .session import DEFAULT_TIMEOUT


def _redirect_to(response: requests.Response) -> str | None:
    redirect_url = None
    for line in response.text.splitlines():
        if "window.location.href" in line and "==" not in line:
            match = re.search(r'window\.location\.href\s*=\s*["\'](.*?)["\']', line)
            if match:
                redirect_url = match.group(1)
                url_split = line.split(redirect_url)
                if len(url_split) >= 2:
                    post_url_line = url_split[-1]
                    if "+" in post_url_line:
                        redirect_url = None
                        continue
                redirect_url = urllib.parse.urljoin(response.url, redirect_url)
                logging.info("Following %s", redirect_url)
                break
    return redirect_url


def _is_cloudflare_challenge(text: str) -> bool:
    indicators = [
        "Just a moment...",
        "__cf_chl_",
        "Enable JavaScript and cookies to continue",
        "cf-browser-verification",
    ]
    return any(ind in text for ind in indicators)


def _fetch_with_playwright(url: str) -> requests.Response | None:
    logging.info("Fetching %s with playwright", url)
    ensure_install()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        resp = None
        try:
            resp = page.goto(url, wait_until="domcontentloaded")
        except:  # noqa: E722
            pass
        if resp is None:
            browser.close()
            return None

        status_code = resp.status
        final_url = resp.url
        headers = resp.headers
        html = page.content()

        browser.close()

    # Build fake requests.Response
    cookies = RequestsCookieJar()
    mock_response = Response()
    mock_response.status_code = status_code
    mock_response._content = html.encode("utf-8")
    mock_response.headers = CaseInsensitiveDict(headers)
    mock_response.url = final_url
    mock_response.cookies = cookies
    mock_response.raw = HTTPResponse(
        body=BytesIO(html.encode("utf-8")),
        status=status_code,
        headers=CaseInsensitiveDict(headers),
        preload_content=False,
    )
    request = Request(
        method="GET",
        url=url,
        headers=None,
        cookies=cookies,
    )
    prepared_request = request.prepare()
    prepared_request.prepare_cookies(cookies)
    mock_response.request = prepared_request

    return mock_response


class ScrapeSession(requests_cache.CachedSession):
    """A requests session that can rotate between different proxies."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._proxies = []
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._last_fetched = None
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        self._user_agent_rotator = UserAgent(
            software_names=software_names, operating_systems=operating_systems
        )
        self._wayback_client = wayback.WaybackClient()
        self._wayback_disabled = False
        self.fast_fail_urls = set()
        self._session = requests_cache.CachedSession(*args, **kwargs)
        self._session.cookies.set_policy(BlockAll())
        self._args = args
        self._kwargs = kwargs

    def _suggest_proxy(self) -> str:
        proxies = self._proxies
        if (
            not proxies
            or self._last_fetched is None
            or (
                self._last_fetched
                < datetime.datetime.now() - datetime.timedelta(minutes=30)
            )
        ):
            proxies = [""]  # This indicates that no proxy is used
            proxies_txt = os.environ.get("PROXIES")
            if proxies_txt is not None:
                proxies.extend(proxies_txt.split(","))
            random.shuffle(proxies)
            self._proxies = proxies
            self._last_fetched = datetime.datetime.now()

        proxy = random.choices(
            population=proxies,
            weights=np.linspace(1.0, 0.0, len(proxies)).tolist(),
            k=1,
        )
        return proxy[0]

    def _wayback_machine_request(
        self, method, url, **kwargs
    ) -> requests.Response | None:
        if method.upper() != "GET":
            return None
        try:
            for record in self._wayback_client.search(url, fast_latest=True):
                if record.timestamp.replace(
                    tzinfo=None
                ) < datetime.datetime.now().replace(tzinfo=None) - datetime.timedelta(
                    days=350 * 10
                ):
                    continue
                with self._wayback_client.get_memento(record) as memento:  # type: ignore
                    cookies = RequestsCookieJar()
                    response = Response()
                    response.status_code = memento.status_code
                    response._content = memento.content
                    response.url = url
                    response.headers = memento.headers  # type: ignore
                    response.cookies = cookies
                    response.raw = HTTPResponse(
                        body=BytesIO(memento.content),
                        status=memento.status_code,
                        headers=memento.headers,
                        preload_content=False,
                    )

                    request = Request(
                        method=method,
                        url=url,
                        headers=kwargs.get("headers"),
                        cookies=cookies,
                    )
                    prepared_request = request.prepare()
                    prepared_request.prepare_cookies(cookies)
                    response.request = prepared_request

                    return response
        except (
            wayback.exceptions.MementoPlaybackError,  # pyright: ignore
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ContentDecodingError,
        ):  # pyright: ignore
            pass
        return None

    @func_set_timeout(DEFAULT_TIMEOUT)
    def _perform_timeout_send(
        self, request: requests.PreparedRequest, no_wayback: bool, **kwargs
    ) -> Any:
        key = self.cache.create_key(request)

        if not self.settings.disabled:
            # Check the cache
            cached_response = self.cache.get_response(key)
            if cached_response:
                return cached_response

            logging.info(
                "Request for %s not cached (no-wayback: %s).",
                request.url,
                str(no_wayback),
            )

            # Otherwise check the wayback machine
            if not self._is_fast_fail_url(request.url) and not no_wayback:
                response = self._wayback_machine_request(
                    request.method, request.url, headers=request.headers
                )
                if response is not None and response.ok:
                    logging.info(
                        "Found wayback machine memento for URL: %s", request.url
                    )
                    self.cache.save_response(response=response, cache_key=key)
                    return response
        else:
            logging.info("Request for %s caching disabled.", request.url)

        response = self._session.send(request, **kwargs)

        if (
            response.status_code == http.HTTPStatus.FORBIDDEN
            and (
                _is_cloudflare_challenge(response.text)
                or "<H1>Access Denied</H1>" in response.text
            )
            and request.url is not None
        ):
            playwright_response = _fetch_with_playwright(request.url)
            if playwright_response is not None:
                response = playwright_response
                if not self.settings.disabled:
                    self.cache.save_response(response=response, cache_key=key)

        if response.status_code == http.HTTPStatus.FORBIDDEN:
            logging.info("Recreating session due to 403 on %s", request.url)
            self._session = requests_cache.CachedSession(*self._args, **self._kwargs)
            self._session.cookies.set_policy(BlockAll())

        if not self._is_fast_fail_url(response.url):
            response.raise_for_status()
        return response

    @retry(
        stop=stop_after_attempt(128),
        after=after_log(logging.getLogger(__name__), logging.DEBUG),
        before=before_log(logging.getLogger(__name__), logging.DEBUG),
        wait=wait_random_exponential(multiplier=1, max=240),
        retry=retry_if_exception_type(FunctionTimedOut)
        | retry_if_exception_type(requests.exceptions.ProxyError)
        | retry_if_exception_type(requests.exceptions.ConnectionError)
        | retry_if_exception_type(requests.exceptions.ChunkedEncodingError)
        | retry_if_exception_type(ValueError)
        | retry_if_exception_type(requests.exceptions.HTTPError)
        | retry_if_exception_type(requests.exceptions.ReadTimeout)
        | retry_if_exception_type(sqlite3.OperationalError),
        reraise=True,
    )
    def _perform_retry_send(
        self, request: requests.PreparedRequest, no_wayback: bool, **kwargs
    ) -> Any:
        return self._perform_timeout_send(request, no_wayback, **kwargs)

    def send(
        self,
        request: PreparedRequest,
        expire_after: ExpirationTime = None,  # pyright: ignore
        only_if_cached: bool = False,
        refresh: bool = False,
        force_refresh: bool = False,
        **kwargs,
    ) -> AnyResponse:
        if self._is_fast_fail_url(request.url):
            response = super().send(
                request,
                expire_after=expire_after,
                only_if_cached=only_if_cached,
                refresh=refresh,
                force_refresh=force_refresh,
                **kwargs,
            )
            self.cache.save_response(response)
            return response

        return self._perform_retry_send(
            request,
            self._wayback_disabled,
            expire_after=expire_after,
            only_if_cached=only_if_cached,
            refresh=refresh,
            force_refresh=force_refresh,
            **kwargs,
        )

    def request(  # type: ignore
        self,
        method: str,
        url: str,
        *args,
        headers: Optional[MutableMapping[str, str]] = None,
        expire_after: ExpirationTime = None,  # pyright: ignore
        only_if_cached: bool = False,
        refresh: bool = False,
        force_refresh: bool = False,
        **kwargs,
    ) -> AnyResponse:
        if "timeout" not in kwargs:
            if self._is_fast_fail_url(url):
                kwargs["timeout"] = 5.0
            else:
                kwargs["timeout"] = DEFAULT_TIMEOUT
        if headers is None:
            headers = {}
        if "User-Agent" not in headers:
            headers["User-Agent"] = (
                self._user_agent_rotator.get_random_user_agent().strip()
            )
        proxy = self._suggest_proxy()
        if proxy:
            logging.debug("Using proxy: %s", proxy)
            kwargs.setdefault(
                "proxies",
                {
                    "http": proxy,
                    "https": proxy,
                },
            )
        response = super().request(
            method,
            url,
            *args,
            headers=headers,
            expire_after=expire_after,
            only_if_cached=only_if_cached,
            refresh=refresh,
            force_refresh=force_refresh,
            **kwargs,
        )
        redirects = 0
        while (redirect_url := _redirect_to(response)) is not None:
            response = super().request(
                method,
                redirect_url,
                *args,
                headers=headers,
                expire_after=expire_after,
                only_if_cached=only_if_cached,
                refresh=refresh,
                force_refresh=force_refresh,
                **kwargs,
            )
            redirects += 1
            if redirects >= 10:
                break

        return response

    @contextmanager
    def wayback_disabled(self):
        """Disable lookups on the wayback machine."""
        old_state = self._wayback_disabled
        self._wayback_disabled = True
        try:
            yield
        finally:
            self._wayback_disabled = old_state

    def _is_fast_fail_url(self, url: str | None) -> bool:
        if url is None:
            return False
        for fast_fail_domain in self.fast_fail_urls:
            if url.startswith(fast_fail_domain):
                return True
        return False


def create_scrape_session(
    name: str, fast_fail_urls: set[str] | None = None
) -> ScrapeSession:
    """Creates a standard scrape session."""
    session = ScrapeSession(
        name,
        expire_after=requests_cache.NEVER_EXPIRE,
        allowable_methods=("GET", "HEAD", "POST"),
        stale_if_error=True,
    )
    if fast_fail_urls is not None:
        session.fast_fail_urls = fast_fail_urls
    return session
