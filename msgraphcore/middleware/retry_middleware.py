import sys
import time

from msgraphcore.middleware.middleware import BaseMiddleware
from msgraphcore.middleware.utils import get_retry_after


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
    _DEFAULT_RETRY_CODES = [429, 503, 504]

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

    @classmethod
    def disable_retries(cls):
        """
        Disable retry functionality by setting total number of retries to allow to zero
        Retry total takes precedence over all other counts.
        """
        return cls(retry_configs={"retry_total": 0})

    def configure_retry_settings(self):
        """Configure retry settings into the form of a dict."""
        return {
            'total': self.total_retries,
            'backoff': self.backoff_factor,
            'max_backoff': self.backoff_max,
            'methods': self._allowed_methods,
            'timeout': self.timeout,
        }

    def send(self, request, **kwargs):
        """
        Sends the http request object to the next middleware or retries the request if necessary.
        """
        retry_settings = self.configure_retry_settings()
        retry_active = True
        response = None

        while retry_active:
            try:
                request.headers.update({'retry-attempt': '{}'.format(self._retry_count)})
                response = super().send(request, **kwargs)
                # Check if the request needs to be retried based on the response
                if self.should_retry(retry_settings, response):
                    retry_active = self.increment_counter(retry_settings)
                    if retry_active:
                        self.sleep(retry_settings, response=response)
                        continue
                break
            except Exception as error:
                raise error
        return response

    def should_retry(self, retry_settings, response):
        """
        Determines whether the request should be retried
        Checks if the request method is in allowed methods
        Checks if the response status code is in retryable status codes.
        """
        if not self._is_method_retryable(retry_settings, response.request):
            return False
        return retry_settings['total'] and response.status_code in self._retry_on_status_codes

    def _is_method_retryable(self, retry_settings, request):
        """
        Checks if a given request should be retried upon, depending on
        whether the HTTP method is in the set of allowed methods
        """
        if request.method.upper() not in retry_settings['methods']:
            return False
        return True

    def increment_counter(self, retry_settings):
        """
        Increment the retry counters on every valid retry
        """
        if self.retries_exhausted(retry_settings):
            return False
        retry_settings['total'] -= 1
        self._retry_count += 1
        return True

    def retries_exhausted(self, retry_settings):
        retry_counts = retry_settings['total']
        if retry_counts <= 0:
            return True
        return False

    def sleep(self, retry_settings, response=None):
        """
        Sleep between retry attempts.
        Respects a retry-after header in the response if provided
        If no retry-after response header, it defaults to exponential backoff
        """
        if response:
            slept = self._sleep_based_on_retry_after(response)
            if slept:
                return
        self._sleep_exp_backoff(retry_settings)

    def _sleep_based_on_retry_after(self, response):
        """
        Sleep between retries based on the retry-after response header value.
        """
        retry_after = get_retry_after(response)
        if retry_after:
            time.sleep(retry_after)
            return True
        return False

    def _sleep_exp_backoff(self, retry_settings):
        """
        Sleep using exponential backoff value.
        Immediately returns if backoff is 0.
        """
        exp_backoff_value = retry_settings['backoff'] * (2**self._retry_count)
        backoff = min(retry_settings['max_backoff'], exp_backoff_value)
        if backoff <= 0:
            return
        time.sleep(backoff)
