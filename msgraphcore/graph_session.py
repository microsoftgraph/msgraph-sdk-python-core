"""
Graph Session
"""
from requests import Session, Request, Response

from msgraphcore.constants import BASE_URL, SDK_VERSION
from msgraphcore.middleware._middleware import MiddlewarePipeline, BaseMiddleware
from msgraphcore.middleware._base_auth import AuthProviderBase
from msgraphcore.middleware.authorization import AuthorizationHandler


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

    def get(self, url: str, **kwargs) -> Response:
        return self._prepare_and_send_request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> Response:
        return self._prepare_and_send_request('POST', url, **kwargs)

    def put(self, url: str, **kwargs) -> Response:
        return self._prepare_and_send_request('PUT', url, **kwargs)

    def patch(self, url: str, **kwargs) -> Response:
        return self._prepare_and_send_request('PATCH', url, **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        return self._prepare_and_send_request('DELETE', url, **kwargs)

    def _get_url(self, url: str) -> Response:
        return self._base_url+url if (url[0] == '/') else url

    def _register(self, middleware: [BaseMiddleware]) -> None:
        if middleware:
            middleware_adapter = MiddlewarePipeline()

            for ware in middleware:
                middleware_adapter.add_middleware(ware)

            self.mount('https://', middleware_adapter)

    def _prepare_and_send_request(self, method: str = '', url: str = '', **kwargs) -> Response:
        # Retrieve middleware options
        list_of_scopes = kwargs.pop('scopes', None)

        # Prepare request
        request_url = self._get_url(url)
        request = Request(method, request_url, kwargs)
        prepared_request = self.prepare_request(request)

        if list_of_scopes is not None:
            # Append middleware options to the request object, will be used by MiddlewareController
            prepared_request.scopes = list_of_scopes

        return self.send(prepared_request, **kwargs)
