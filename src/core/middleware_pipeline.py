from requests.adapters import HTTPAdapter


class MiddlewarePipeline(HTTPAdapter):
    def __init__(self):
        super(MiddlewarePipeline, self).__init__(self)
        self._head = None

    def add_middleware(self, middleware):
        if self._head is None:
            self._head = middleware
            return

        self._head._next = middleware

    def send(self, request, **kwargs):
        if self._head is not None:
            return self._head.send(request, **kwargs)
        return super().send(request, **kwargs)
