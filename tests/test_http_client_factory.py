from unittest import TestCase

from requests_middleware import BaseMiddleware, MiddlewareHTTPAdapter

from src.core.http_client_factory import HTTPClientFactory


class HTTPClientFactoryTest(TestCase):
    def test_initialized_with_middlewares(self):
        middlewares = [
            BaseMiddleware()
        ]

        requests = HTTPClientFactory.with_graph_middlewares(middlewares)
        mocked_middleware = requests.get_adapter('https://')

        self.assertIsInstance(mocked_middleware, MiddlewareHTTPAdapter)

    def test_created_with_authentication_provider(self):
        """
        TODO: Implement create with authentication provider
        :return:
        """
        pass
