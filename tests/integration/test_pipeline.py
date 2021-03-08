import warnings
from unittest import TestCase

from msgraphcore.graph_session import GraphSession

URL = 'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'


class MiddlewarePipelineTest(TestCase):
    def setUp(self):
        warnings.filterwarnings(
            "ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>"
        )

    def test_middleware_pipeline(self):

        scopes = ['user.read']
        credential = _CustomTokenCredential()
        graph_session = GraphSession(credential, scopes)
        result = graph_session.get(URL)

        self.assertEqual(result.status_code, 200)


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']
