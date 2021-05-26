import ssl
import uuid

from requests.adapters import HTTPAdapter
from urllib3 import PoolManager

from msgraphcore.middleware.request_context import RequestContext


class MiddlewarePipeline(HTTPAdapter):
    """MiddlewarePipeline, entry point of middleware

    The pipeline is implemented as a linked-list, read more about
    it here https://buffered.dev/middleware-python-requests/
    """
    def __init__(self):
        super().__init__()
        self._middleware = None
        self.poolmanager = PoolManager(ssl_version=ssl.PROTOCOL_TLSv1_2)

    def add_middleware(self, middleware):
        if self._middleware_present():
            self._middleware.next = middleware
        else:
            self._middleware = middleware

    def send(self, request, **kwargs):

        if not hasattr(request, 'context'):
            headers = request.headers
            request.context = RequestContext(dict(), headers)

        if self._middleware_present():
            return self._middleware.send(request, **kwargs)
        # No middleware in pipeline, call superclass' send
        return super().send(request, **kwargs)

    def _middleware_present(self):
        return self._middleware


class BaseMiddleware(HTTPAdapter):
    """Base class for middleware

    Handles moving a Request to the next middleware in the pipeline.
    If the current middleware is the last one in the pipeline, it
    makes a network request
    """
    def __init__(self):
        super().__init__()
        self.next = None

    def send(self, request, **kwargs):
        if self.next is None:
            return super().send(request, **kwargs)
        return self.next.send(request, **kwargs)
