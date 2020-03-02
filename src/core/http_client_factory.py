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

        adapter = MiddlewareHTTPAdapter(kwargs.get('middlewares'))
        self.mount('https://', adapter)

    def get(self, url, **kwargs):
        graph_url = self._base_url+url
        super(_HTTPClient, self).get(graph_url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        graph_url = self._base_url+url
        super(_HTTPClient, self).post(graph_url, data=None, json=None, **kwargs)

    def put(self, url, data=None, **kwargs):
        graph_url = self._base_url+url
        super(_HTTPClient, self).put(graph_url, data=None, **kwargs)

    def patch(self, url, data=None, **kwargs):
        graph_url = self._base_url+url
        super(_HTTPClient, self).patch(graph_url, data=None, **kwargs)

    def delete(self, url, **kwargs):
        graph_url = self._base_url+url
        super(_HTTPClient, self).delete(graph_url, **kwargs)
