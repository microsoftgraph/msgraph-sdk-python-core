import warnings
from unittest import TestCase

from msgraphcore.graph_session import GraphSession
from msgraphcore.middleware.authorization import AuthProviderBase


class MiddlewarePipelineTest(TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

    def test_middleware_pipeline(self):
        url = 'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
        scopes = ['user.read']
        auth_provider = _CustomAuthProvider(scopes)
        graph_session = GraphSession(auth_provider)
        result = graph_session.get(url)

        self.assertEqual(result.status_code, 200)


class _CustomAuthProvider(AuthProviderBase):
    def __init__(self, scopes):
        pass

    def get_access_token(self):
        return '{token:https://graph.microsoft.com/}'



