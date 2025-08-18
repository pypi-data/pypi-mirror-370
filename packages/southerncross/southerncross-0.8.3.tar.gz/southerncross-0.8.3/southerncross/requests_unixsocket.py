import socket

import requests
from requests.adapters import HTTPAdapter
from requests.compat import urlparse, unquote

try:
    from requests.packages import urllib3
except ImportError:
    import urllib3


DEFAULT_SCHEME = "http+unix://"
_user_agent = None


# The following was adapted from some code from docker-py
# https://github.com/docker/docker-py/blob/master/docker/transport/unixconn.py
class UnixHTTPConnection(urllib3.connection.HTTPConnection):
    def __init__(self, unix_socket_url, timeout=60):
        """Create an HTTP connection to a unix domain socket

        :param unix_socket_url: A URL with a scheme of 'http+unix' and the
        netloc is a percent-encoded path to a unix domain socket. E.g.:
        'http+unix://%2Ftmp%2Fprofilesvc.sock/status/pid'
        """
        super().__init__("localhost", timeout=timeout)
        self.unix_socket_url = unix_socket_url
        self.timeout = timeout
        self.sock = None

    def __del__(self):      # Base class does not have d'tor.
        if self.sock:
            self.sock.close()

    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        socket_path = unquote(urlparse(self.unix_socket_url).netloc)
        sock.connect(socket_path)
        self.sock = sock


class UnixHTTPConnectionPool(urllib3.connectionpool.HTTPConnectionPool):
    def __init__(self, socket_path, timeout=60):
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path
        self.timeout = timeout

    def _new_conn(self):
        return UnixHTTPConnection(self.socket_path, self.timeout)


class UnixAdapter(HTTPAdapter):
    def __init__(self, timeout=60, pool_connections=25, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout
        self.pools = urllib3._collections.RecentlyUsedContainer(
            pool_connections, dispose_func=lambda p: p.close()
        )

    def get_connection(self, url, proxies=None):
        proxies = proxies or {}
        proxy = proxies.get(urlparse(url.lower()).scheme)

        if proxy:
            raise ValueError("%s does not support specifying proxies" % self.__class__.__name__)

        with self.pools.lock:
            pool = self.pools.get(url)
            if pool:
                return pool

            pool = UnixHTTPConnectionPool(url, self.timeout)
            self.pools[url] = pool

        return pool

    def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None):
        # Fix for requests 2.32.2+.
        # https://github.com/psf/requests/commit/c98e4d133ef29c46a9b68cd783087218a8075e05
        return self.get_connection(request.url, proxies)

    def request_url(self, request, proxies):
        return request.path_url

    def close(self):
        self.pools.clear()


def set_user_agent(name):
    global _user_agent
    _user_agent = name


class Session(requests.Session):
    def __init__(self, url_scheme=DEFAULT_SCHEME, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mount(url_scheme, UnixAdapter())

        if _user_agent:
            self.headers["User-Agent"] = _user_agent


def request(method, url, **kwargs):
    session = Session()
    return session.request(method=method, url=url, **kwargs)


def get(url, **kwargs):
    return request("get", url, **kwargs)


def head(url, **kwargs):
    return request("head", url, **kwargs)


def post(url, **kwargs):
    return request("post", url, **kwargs)


def patch(url, **kwargs):
    return request("patch", url, **kwargs)


def put(url, **kwargs):
    return request("put", url, **kwargs)


def delete(url, **kwargs):
    return request("delete", url, **kwargs)


def options(url, **kwargs):
    return request("options", url, **kwargs)
