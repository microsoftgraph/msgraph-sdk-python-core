import ssl

from requests.adapters import HTTPAdapter
from urllib3 import PoolManager

class MiddlewarePipeline(HTTPAdapter):
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
        if self._middleware_present():
            return self._middleware.send(request, **kwargs)
        # No middleware in pipeline, call superclass' send
        return super().send(request, **kwargs)

    def _middleware_present(self):
        return self._middleware

