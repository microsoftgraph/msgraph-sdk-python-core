"""
Graph Session
"""
from pprint import pprint

from requests import Session, Request, Response

from msgraphcore.constants import BASE_URL, SDK_VERSION
from msgraphcore.middleware._middleware import MiddlewarePipeline, BaseMiddleware
from msgraphcore.middleware._base_auth import AuthProviderBase
from msgraphcore.middleware.authorization import AuthorizationHandler


def _get_middleware_options(func):
    def wrapper(*args, **kwargs):
        scopes = kwargs.pop('scopes')
        print(scopes)
        return func(*args, **kwargs)
    return wrapper


class GraphSession(Session):
    """
    Extends session object with graph functionality
    """
    def __init__(self, auth_provider: AuthProviderBase, middleware: list = []):
        super().__init__()
        self.headers.update({'sdkVersion': 'graph-python-' + SDK_VERSION})
        self._base_url = BASE_URL

        auth_handler = AuthorizationHandler(auth_provider)

        middleware.insert(0, auth_handler)
        self._register(middleware)

    @_get_middleware_options
    def get(self, url, **kwargs):
        return super().get(self._graph_url(url))

    @_get_middleware_options
    def post(self, url, data=None, json=None, **kwargs):
        return super().post(self._graph_url(url), data, json, **kwargs)

    @_get_middleware_options
    def put(self, url, data=None, **kwargs):
        return super().put(self._graph_url(url), data, **kwargs)

    @_get_middleware_options
    def patch(self, url, data=None, **kwargs):
        return super().patch(self._graph_url(url), data, **kwargs)

    @_get_middleware_options
    def delete(self, url, **kwargs):
        return super().delete(url, **kwargs)

    def _graph_url(self, url: str) -> Response:
        return self._base_url+url if (url[0] == '/') else url

    def _register(self, middleware: [BaseMiddleware]) -> None:
        if middleware:
            middleware_adapter = MiddlewarePipeline()

            for ware in middleware:
                middleware_adapter.add_middleware(ware)

            self.mount('https://', middleware_adapter)

    def _prepare_and_send_request(self, method: str = '', url: str = '', data=None, json=None, **kwargs) -> Response:
        # Retrieve middleware options
        list_of_scopes = kwargs.pop('scopes', None)

        # Prepare request
        request_url = self._graph_url(url)
        request = Request(method, request_url, data=data, json=json, **kwargs)
        pprint(request.__dict__)
        prepared_request = self.prepare_request(request)

        if list_of_scopes is not None:
            # Append middleware options to the request object, will be used by MiddlewareController
            prepared_request.scopes = list_of_scopes

        return self.send(prepared_request, **kwargs)



