"""A cookie policy that rejects all cookies."""

# pylint: disable=unused-argument
from http import cookiejar


class BlockAll(cookiejar.CookiePolicy):
    """Blocks all cookies from being registered."""

    def _noop(self, *args, **kwargs):
        return False

    return_ok = set_ok = domain_return_ok = path_return_ok = _noop
    netscape = True
    rfc2965 = hide_cookie2 = False
