"""Tests for the scrape session class."""
import datetime
import http
import unittest
from unittest.mock import MagicMock

import wayback.exceptions

from scrapesession.scrapesession import ScrapeSession
import wayback


class TestScrapeSession(unittest.TestCase):

    def setUp(self):
        self.session = ScrapeSession("test")

    def test_wayback(self):
        url = "https://www.thing.com"
        timestamp = int(datetime.datetime.now().timestamp())
        status_code = http.HTTPStatus.OK
        wayback_client = wayback.WaybackClient()
        record = wayback.CdxRecord(
            "",
            timestamp,
            url,
            "",
            status_code,
            "",
            0,
            "https://web.archive.org/web/19961231235847id_/http://www.nasa.gov/",
            "https://web.archive.org/web/19961231235847/http://www.nasa.gov/",
        )
        memento = wayback.Memento(
            url=url,
            timestamp=timestamp,
            mode=wayback.Mode.original,
            memento_url="",
            status_code=status_code,
            headers={},
            encoding="utf8",
            raw=None,
            raw_headers={},
            links=[],
            history=[],
            debug_history=[],
        )
        wayback_client.search = MagicMock(return_value=[record])
        wayback_client.get_memento = MagicMock(return_value=memento)
        response = self.session.get(url)
        self.assertTrue(response.ok)

    def test_wayback_raises_exception(self):
        url = "https://www.thing.com"

        def search_exception(*args, **kwargs):
            raise wayback.exceptions.MementoPlaybackError()

        wayback_client = wayback.WaybackClient()
        wayback_client.search = search_exception
        self.session._wayback_client = wayback_client
        response = self.session.get(url)
        self.assertTrue(response.ok)
