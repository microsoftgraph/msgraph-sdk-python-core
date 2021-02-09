from unittest import TestCase

import responses
from requests import Session
from requests.adapters import HTTPAdapter

from msgraphcore.constants import BASE_URL, SDK_VERSION
from msgraphcore.graph_session import GraphSession


class GraphSessionTest(TestCase):
    def setUp(self) -> None:
        self.credential = _CustomTokenCredential()
        self.requests = GraphSession(self.credential, ['user.read'])

    def tearDown(self) -> None:
        self.requests = None

    def test_creates_instance_of_session(self):
        self.assertIsInstance(self.requests, Session)

    def test_has_graph_url_as_base_url(self):
        self.assertNotEqual(self.requests._base_url, BASE_URL)

    def test_has_sdk_version_header(self):
        self.assertTrue('sdkVersion' in self.requests.headers)

    def test_updated_sdk_version(self):
        self.assertTrue(
            self.requests.headers.get('sdkVersion').startswith('graph-python-' + SDK_VERSION)
        )

    def test_initialized_with_middlewares(self):
        graph_session = GraphSession(self.credential)
        mocked_middleware = graph_session.get_adapter('https://')

        self.assertIsInstance(mocked_middleware, HTTPAdapter)

    @responses.activate
    def test_builds_graph_urls(self):
        graph_url = self.requests._base_url + '/me'
        responses.add(responses.GET, graph_url, status=200)

        self.requests.get('/me')
        request_url = responses.calls[0].request.url

        self.assertEqual(graph_url, request_url)

    @responses.activate
    def test_does_not_build_graph_urls_for_full_urls(self):
        other_url = 'https://microsoft.com/'
        responses.add(responses.GET, other_url, status=200)

        self.requests.get(other_url)
        request_url = responses.calls[0].request.url

        self.assertEqual(other_url, request_url)


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']
