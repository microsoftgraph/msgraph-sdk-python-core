import sys
import time

from msgraphcore.middleware.middleware import BaseMiddleware


class RetryMiddleware(BaseMiddleware):
    """
    TransportAdapter that allows us to specify the
    retry policy for all requests
    """
    DEFAULT_DELAY = 3
    MAX_DELAY = 180
    DEFAULT_MAX_RETRIES = 5
    MAX_MAX_RETRIES = 10
    MAXIMUM_BACKOFF = 120
    _DEFAULT_RETRY_CODES = [429, 502, 503, 504]

    def __init__(self, retry_configs=None):
        self.total_retries: int = retry_configs.pop('retry_total', 5)
        self.backoff_factor: float = retry_configs.pop('retry_backoff_factor', 0.1)
        self.backoff_max: int = retry_configs.pop('retry_backoff_max', self.MAXIMUM_BACKOFF)
        self.timeout: int = retry_configs.pop('timeout', 604800)

        status_codes: [int] = retry_configs.pop('retry_on_status_codes', [])

        self._retry_on_status_codes = set(status_codes) | set(self._DEFAULT_RETRY_CODES)
        self._allowed_methods = frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'])
        self._respect_retry_after_header = True
        self._retry_count = 0
