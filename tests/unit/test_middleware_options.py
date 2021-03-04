from unittest import TestCase

from msgraphcore.middleware.options.auth_middleware_options import AuthMiddlewareOptions
from msgraphcore.middleware.options.retry_middleware_options import RetryMiddlewareOptions

retry_config = {
    'retry_total': 5,
    'retry_backoff_factor': 0.8,
    'retry_backoff_max': 100,
    'retry_time_limit': 100,
    'retry_on_status_codes': [502, 503],
}


class TestAuthMiddlewareOptions(TestCase):
    def test_multiple_scopes(self):
        graph_scopes = 'https://graph.microsoft.com/v1.0?scopes=mail.read%20user.read%20'
        auth_options = AuthMiddlewareOptions(graph_scopes)
        self.assertEqual(auth_options.scopes, graph_scopes)


def test_retry_middleware_options():

    retry_options = RetryMiddlewareOptions(retry_config)

    assert retry_config["retry_total"] == retry_options.retry_total
    assert retry_config["retry_backoff_factor"] == retry_options.retry_backoff_factor
    assert retry_config["retry_backoff_max"] == retry_options.retry_backoff_max
    assert retry_config["retry_time_limit"] == retry_options.retry_time_limit
    assert retry_config["retry_on_status_codes"] == retry_options.retry_on_status_codes
