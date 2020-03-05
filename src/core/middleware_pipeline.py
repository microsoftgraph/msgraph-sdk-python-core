import ssl

from requests.adapters import HTTPAdapter
from urllib3 import PoolManager


class MiddlewarePipeline(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self._head = None

    def add_middleware(self, middleware):
        if self._head is None:
            self._head = middleware
            return

        self._head.next = middleware

    def send(self, request, **kwargs):
        if self._head is not None:
            return self._head.send(request, **kwargs)
        return super().send(request, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)
