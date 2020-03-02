from unittest import TestCase

from requests import Session

from src.core.http_client_factory import _HTTPClient
from src.constants import BASE_URL, SDK_VERSION


class HTTPClientTest(TestCase):
    def setUp(self) -> None:
        self.requests = _HTTPClient()

    def tearDown(self) -> None:
        self.requests = None

    def test_creates_instance_of_session(self):
        self.assertIsInstance(self.requests, Session)

    def test_has_graph_url_as_base_url(self):
        self.assertEqual(self.requests._base_url, BASE_URL)

    def test_has_sdk_version_header(self):
        self.assertEqual(self.requests.headers.get('sdkVersion'), SDK_VERSION)

    def test_configure_http_proxy(self):
        """
        TODO: Support HTTP proxies
        :return:
        """
        pass

    def test_gzip_compresses_payloads(self):
        """
        TODO: Compress payloads
        :return:
        """
        pass

    def test_uses_tls_1_point_2(self):
        """
        Use TLS 1.2
        :return:
        """
        pass
