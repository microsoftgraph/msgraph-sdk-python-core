from unittest import TestCase

from requests.adapters import HTTPAdapter

from src.core.http_client_factory import HTTPClientFactory
from src.core.middleware_pipeline import MiddlewarePipeline


class HTTPClientFactoryTest(TestCase):
    def test_initialized_with_middlewares(self):
        middlewares = [
            HTTPAdapter()   # Middlewares inherit from the HTTPAdapter class
        ]

        requests = HTTPClientFactory.with_graph_middlewares(middlewares)
        mocked_middleware = requests.get_adapter('https://')

        self.assertIsInstance(mocked_middleware, MiddlewarePipeline)

    def test_created_with_authentication_provider(self):
        """
        TODO: Implement create with authentication provider
        :return:
        """
        pass
