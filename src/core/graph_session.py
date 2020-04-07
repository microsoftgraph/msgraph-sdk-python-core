"""
Creates a session object
"""
from requests import Session, Request

from src.constants import BASE_URL, SDK_VERSION
from src.middleware._middleware import MiddlewarePipeline


class GraphSession(Session):
    """
    Extends session object with graph functionality
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.headers.update({'sdkVersion': SDK_VERSION})
        self._base_url = BASE_URL
        middleware = kwargs.get('middleware')
        self._register(middleware)

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

    def _register(self, middleware):
        if middleware:
            middleware_adapter = MiddlewarePipeline()

            for ware in middleware:
                middleware_adapter.add_middleware(ware)

            self.mount('https://', middleware_adapter)

    def _prepare_and_send_request(self, method='', url='', **kwargs):
        # Retrieve middleware options
        list_of_scopes = kwargs.pop('scopes', None)

        # Prepare request
        request_url = self._get_url(url)
        request = Request(method, request_url, kwargs)
        prepared_request = self.prepare_request(request)

        if list_of_scopes is not None:
            # prepare scopes middleware option
            graph_scopes = BASE_URL + '?scopes='
            for scope in list_of_scopes:
                graph_scopes += scope + '%20'

            # Append middleware options to the request object, will be used by MiddlewareController
            prepared_request.scopes = graph_scopes

        return self.send(prepared_request, **kwargs)
