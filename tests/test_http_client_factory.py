import unittest

from requests_middleware import BaseMiddleware
from requests.adapters import HTTPAdapter

from src.core.http_client_factory import HTTPClientFactory


class HTTPClientFactoryTest(unittest.TestCase):
    def test_initialized_with_middlewares(self):
        middlewares = [
            _MockMiddleware()
        ]

        requests = HTTPClientFactory.with_graph_middlewares(middlewares)
        _, mocked_middleware = requests.adapters.popitem()

        self.assertIsInstance(mocked_middleware, HTTPAdapter)

    def test_created_with_authentication_provider(self):
        """
        TODO: Implement create with authentication provider
        :return:
        """
        pass


class _MockMiddleware(BaseMiddleware):
    pass
