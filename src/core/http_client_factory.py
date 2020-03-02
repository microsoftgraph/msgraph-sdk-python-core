from requests import Session

from requests_middleware import MiddlewareHTTPAdapter

from src.constants import BASE_URL, SDK_VERSION


class HTTPClientFactory:
    @classmethod
    def with_graph_middlewares(cls, middlewares):
        return _HTTPClient(middlewares=middlewares)


class _HTTPClient(Session):
    def __init__(self, **kwargs):
        super(_HTTPClient, self).__init__()
        self.headers.update({'sdkVersion': SDK_VERSION})
        self._base_url = BASE_URL
        self.adapter = MiddlewareHTTPAdapter(kwargs.get('middlewares'))
