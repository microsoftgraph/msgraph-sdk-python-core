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

