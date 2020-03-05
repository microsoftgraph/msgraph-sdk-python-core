from unittest import TestCase

from requests.adapters import HTTPAdapter
from src.core.http_client_factory import HTTPClientFactory


class MiddlewarePipelineTest(TestCase):
    def test_middleware_pipeline(self):
        url = 'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
        middlewares = [
            _AuthMiddleware()
        ]

        requests = HTTPClientFactory.with_graph_middlewares(middlewares)
        result = requests.get(url)

        self.assertEqual(result.status_code, 200)


class _AuthMiddleware(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self.next = None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        request.headers.update({'Authorization': 'Bearer {token:https://graph.microsoft.com/}'})

        if self.next is None:
            return super().send(request, stream, timeout, verify, cert, proxies)

        response = self.next.send(request, stream, timeout, verify, cert, proxies)
        return response


