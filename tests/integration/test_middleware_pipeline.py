import warnings
from unittest import TestCase

from msgraphcore.graph_session import GraphSession
from msgraphcore.middleware.authorization import AuthProviderBase


class MiddlewarePipelineTest(TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

    def test_middleware_pipeline(self):
        url = 'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'

        auth_provider = _CustomAuthProvider()
        scopes = ['user.read']
        graph_session = GraphSession(scopes, auth_provider)
        result = graph_session.get(url)

        self.assertEqual(result.status_code, 200)


class _CustomAuthProvider(AuthProviderBase):

    def get_access_token(self):
        return '{token:https://graph.microsoft.com/}'



