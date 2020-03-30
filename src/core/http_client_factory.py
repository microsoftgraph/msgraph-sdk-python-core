from requests import Session, Request

from src.constants import BASE_URL, SDK_VERSION
from src.middleware._middleware import MiddlewarePipeline


class HTTPClientFactory:
    @classmethod
    def with_graph_middlewares(cls, middlewares):
        return _HTTPClient(middlewares=middlewares)


class _HTTPClient(Session):
    def __init__(self, **kwargs):
        super().__init__()
        self.headers.update({'sdkVersion': SDK_VERSION})
        self._base_url = BASE_URL
        middlewares = kwargs.get('middlewares')
        self._register(middlewares)

    def get(self, url, **kwargs):
        return self._prepare_and_send_request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self._prepare_and_send_request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self._prepare_and_send_request('PUT', url, **kwargs)

    def patch(self, url, **kwargs):
        return self._prepare_and_send_request('PATCH', url, **kwargs)

    def delete(self, url, **kwargs):
        return self._prepare_and_send_request('DELETE', url, **kwargs)

    def _get_url(self, url):
        return self._base_url+url if (url[0] == '/') else url

    def _prepare_and_send_request(self, method='', url='', **kwargs):
        request_url = self._get_url(url)

        request = Request(method, request_url, kwargs)
        prepared_request = self.prepare_request(request)

        return self.send(prepared_request, **kwargs)

    def _register(self, middlewares):
        if middlewares:
            middleware_adapter = MiddlewarePipeline()

            for middleware in middlewares:
                middleware_adapter.add_middleware(middleware)

            self.mount('https://', middleware_adapter)
