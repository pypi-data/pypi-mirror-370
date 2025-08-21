"""Utilities for AioHTTP framework.

"""

from __future__ import unicode_literals
from appdynamics.lang import parse_qsl

DEFAULT_PORTS = {
    'http': 80,
    'https': 443,
}


def aiohttp_url_parser(string_with_url):
    url = string_with_url.replace("URL(", "").rstrip(")")

    return url


class LazyAioHTTPRequest(object):
    """Lazily read request line and headers from the AioHTTP request environment.

    Attributes
    ----------
    headers : dict
        A dictionary of the HTTP headers. The headers are lowercase with
        dashes separating words.
    method : str
        The request method (e.g., GET).
    url : str
        The URL of the request (reconstructed according to PEP 333).
    cookies : dict
        The cookies passed in the request header (if any).
    path : str
        The path part of the request. Note that unlike raw WSGI, this will be
        just '/' if it would otherwise be empty.
    args : dict
        The query parameters. This is not a multi-dict: if a parameter is
        repeated multiple times, one of them wins.
    referer : str
        The HTTP Referer string.
    user_agent : str
        The HTTP User-Agent string.
    is_ajax : bool
        True if this request is AJAX.
    is_mobile : bool
        True if this request is from mobile.

    """
    DEFAULT_PORTS = {
        'http': 80,
        'https': 443,
    }

    def __init__(self, request):
        super(LazyAioHTTPRequest, self).__init__()
        self.request = request

        self._headers = None
        self._host = None
        self._port = None
        self._http_host = None
        self._url = None
        self._path = None
        self._args = None
        self._cookies = None

    @property
    def headers(self):
        if self._headers is not None:
            return self._headers

        headers = {}
        for key, value in self.request.headers.items():
            header_name = key.lower()
            headers[header_name] = value

        self._headers = headers
        return headers

    @property
    def method(self):
        return self.request.method

    @property
    def is_secure(self):
        return self.request.secure

    @property
    def host(self):
        if self._host is not None:
            return self._host

        self._host = self.request.host

        return self._host

    @property
    def url(self):
        if self._url is not None:
            return self._url

        self._url = aiohttp_url_parser(self.request.url)
        return self._url

    @property
    def cookies(self):
        if self._cookies is not None:
            return self._cookies

        cookies = self.request.cookies

        self._cookies = cookies
        return cookies

    @property
    def path(self):
        if self._path is not None:
            return self._path

        self._path = self.request.path
        return self._path

    @property
    def args(self):
        if self._args is not None:
            return self._args

        query_string = self.request.query_string
        self._args = dict((k, v) for k, v in parse_qsl(query_string))
        return self._args

    @property
    def referer(self):
        return self.request.headers.get('referer')

    @property
    def user_agent(self):
        return self.request.headers.get('user-agent')

    @property
    def is_ajax(self):
        rum_header = self.request.get('HTTP_ADRUM')
        if rum_header and 'isAjax:true' in rum_header:
            return True
        x_requested_header = self.request.get('HTTP_X_REQUESTED_WITH')
        if x_requested_header == 'XMLHttpRequest':
            return True
        return False

    @property
    def is_mobile(self):
        rum_header = self.request.get('HTTP_ADRUM_1')
        return rum_header and 'isMobile:true' in rum_header

    @property
    def server_port(self):
        if self._port is not None:
            return self._port

        host = self.request.host
        port = host.split(':')[1] if ':' in host else '80'

        self._port = port
        return self._port
