from requests import Session

from src.constants import BASE_URL, SDK_VERSION
from .middleware_pipeline import MiddlewarePipeline


class HTTPClientFactory:
    @classmethod
    def with_graph_middlewares(cls, middlewares):
        return _HTTPClient(middlewares=middlewares)


class _HTTPClient(Session):
    def __init__(self, **kwargs):
        super(_HTTPClient, self).__init__()
        self.headers.update({'sdkVersion': SDK_VERSION})
        self._base_url = BASE_URL
        middlewares = kwargs.get('middlewares')

        middleware_adapter = MiddlewarePipeline()

        for middleware in middlewares:
            middleware_adapter.add_middleware(middleware)

        self.mount('https://', middleware_adapter)
        self.mount('http://', middleware_adapter)

    def get(self, url, **kwargs):
        request_url = self._get_url(url)
        super(_HTTPClient, self).get(request_url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        request_url = self._get_url(url)
        super(_HTTPClient, self).post(request_url, data=None, json=None, **kwargs)

    def put(self, url, data=None, **kwargs):
        request_url = self._get_url(url)
        super(_HTTPClient, self).put(request_url, data=None, **kwargs)

    def patch(self, url, data=None, **kwargs):
        request_url = self._get_url(url)
        super(_HTTPClient, self).patch(request_url, data=None, **kwargs)

    def delete(self, url, **kwargs):
        request_url = self._get_url(url)
        super(_HTTPClient, self).delete(request_url, **kwargs)

    def _get_url(self, url):
        return self._base_url+url if (url[0] == '/') else url

