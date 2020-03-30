from requests.adapters import HTTPAdapter


class Middleware(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self.next = None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        if self.next is None:
            return super().send(request, stream, timeout, verify, cert, proxies)

        return self.next.send(request, stream, timeout, verify, cert, proxies)