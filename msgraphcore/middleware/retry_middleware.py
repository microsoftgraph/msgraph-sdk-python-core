import datetime
import random
import sys
import time
from email.utils import parsedate_to_datetime

from msgraphcore.middleware.middleware import BaseMiddleware
from msgraphcore.middleware.options.middleware_control import middleware_control


class RetryMiddleware(BaseMiddleware):
    """
    TransportAdapter that allows us to specify the
    retry policy for all requests
    """

    DEFAULT_TOTAL_RETRIES = 3
    MAX_TOTAL_RETRIES = 10
    DEFAULT_BACKOFF_FACTOR = 0.5
    DEFAULT_RETRY_TIME_LIMIT = 180
    MAXIMUM_BACKOFF = 120
    _DEFAULT_RETRY_CODES = {429, 503, 504}

    def __init__(self, retry_configs={}):
        super().__init__()
        self.total_retries: int = min(
            retry_configs.pop('retry_total', self.DEFAULT_TOTAL_RETRIES), self.MAX_TOTAL_RETRIES
        )
        self.backoff_factor: float = retry_configs.pop(
            'retry_backoff_factor', self.DEFAULT_BACKOFF_FACTOR
        )
        self.backoff_max: int = retry_configs.pop('retry_backoff_max', self.MAXIMUM_BACKOFF)
        self.timeout: int = retry_configs.pop('retry_time_limit', self.DEFAULT_RETRY_TIME_LIMIT)

        status_codes: [int] = retry_configs.pop('retry_on_status_codes', [])

        self._retry_on_status_codes = set(status_codes) | self._DEFAULT_RETRY_CODES
        self._allowed_methods = frozenset(
            ['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
        )
        self._respect_retry_after_header = True

    @classmethod
    def disable_retries(cls):
        """
        Disable retries by setting retry_total to zero.
        retry_total takes precedence over all other counts.
        """
        return cls(retry_configs={"retry_total": 0})

    def get_retry_options(self):
        """
        Check if request specific configs have been passed and override any session defaults
        Then configure retry settings into the form of a dict.
        """
        retry_config_options = middleware_control.get('RETRY_MIDDLEWARE_OPTIONS')
        if retry_config_options:
            return {
                'total':
                min(retry_config_options.retry_total, self.MAX_TOTAL_RETRIES)
                if retry_config_options.retry_total is not None else self.total_retries,
                'backoff':
                retry_config_options.retry_backoff_factor
                if retry_config_options.retry_backoff_factor is not None else self.backoff_factor,
                'max_backoff':
                retry_config_options.retry_backoff_max
                if retry_config_options.retry_backoff_max is not None else self.backoff_max,
                'timeout':
                retry_config_options.retry_time_limit
                if retry_config_options.retry_time_limit is not None else self.timeout,
                'retry_codes':
                set(retry_config_options.retry_on_status_codes)
                | set(self._DEFAULT_RETRY_CODES) if retry_config_options.retry_on_status_codes
                is not None else self._retry_on_status_codes,
                'methods':
                self._allowed_methods,
            }
        return {
            'total': self.total_retries,
            'backoff': self.backoff_factor,
            'max_backoff': self.backoff_max,
            'timeout': self.timeout,
            'retry_codes': self._retry_on_status_codes,
            'methods': self._allowed_methods,
        }

    def send(self, request, **kwargs):
        """
        Sends the http request object to the next middleware or retries the request if necessary.
        """
        retry_options = self.get_retry_options()
        retry_active = True
        absolute_time_limit = retry_options['timeout']
        response = None
        retry_count = 0

        while retry_active:
            try:
                start_time = time.time()
                request.headers.update({'Retry-Attempt': '{}'.format(retry_count)})
                response = super().send(request, **kwargs)
                # Check if the request needs to be retried based on the response
                if self.should_retry(retry_options, response):
                    retry_active = self.increment_counter(retry_options)
                    # Get the delay time between retries
                    sleep_time = self.get_sleep_time(retry_options, retry_count, response)
                    if retry_active and sleep_time < absolute_time_limit:
                        time.sleep(sleep_time)
                        end_time = time.time()
                        absolute_time_limit -= (end_time - start_time)
                        retry_count += 1
                        continue
                break
            except Exception as error:
                raise error
        return response

    def should_retry(self, retry_options, response):
        """
        Determines whether the request should be retried
        Checks if the request method is in allowed methods
        Checks if the response status code is in retryable status codes.
        """
        if not self._is_method_retryable(retry_options, response.request):
            return False
        if not self._is_request_payload_buffered(response):
            return False
        return retry_options['total'] and response.status_code in retry_options['retry_codes']

    def _is_method_retryable(self, retry_options, request):
        """
        Checks if a given request should be retried upon, depending on
        whether the HTTP method is in the set of allowed methods
        """
        if request.method.upper() not in retry_options['methods']:
            return False
        return True

    def _is_request_payload_buffered(self, response):
        """
        Checks if the request payload is buffered/rewindable.
        Payloads with forward only streams will return false and have the responses
        returned without any retry attempt.
        """
        if response.request.method.upper() in frozenset(['HEAD', 'GET', 'DELETE', 'OPTIONS']):
            return True
        if response.request.headers['Content-Type'] == "application/octet-stream":
            return False
        return True

    def increment_counter(self, retry_options):
        """
        Increment the retry counters on every valid retry
        """
        if self.retries_exhausted(retry_options):
            return False
        retry_options['total'] -= 1
        return True

    def retries_exhausted(self, retry_options):
        retries_remaining = retry_options['total']
        if retries_remaining <= 0:
            return True
        return False

    def get_sleep_time(self, retry_options, retry_count, response=None):
        """
        Get the time in seconds to sleep between retry attempts.
        Respects a retry-after header in the response if provided
        If no retry-after response header, it defaults to exponential backoff
        """
        retry_after = self._get_retry_after(response)
        if retry_after:
            return retry_after
        return self._get_sleep_time_exp_backoff(retry_options, retry_count)

    def _get_sleep_time_exp_backoff(self, retry_options, retry_count):
        """
        Get time to sleep based on exponential backoff value.
        """
        exp_backoff_value = retry_options['backoff'] * +(2**(retry_count - 1))
        backoff_value = exp_backoff_value + (random.randint(0, 1000) / 1000)

        backoff = min(retry_options['max_backoff'], backoff_value)
        return backoff

    def _get_retry_after(self, response):
        """
        Check if retry-after is specified in the response header and get the value
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            return self._parse_retry_after(retry_after)
        return None

    def _parse_retry_after(self, retry_after):
        """
        Helper to parse Retry-After and get value in seconds.
        """
        try:
            delay = int(retry_after)
        except ValueError:
            # Not an integer? Try HTTP date
            retry_date = parsedate_to_datetime(retry_after)
            delay = (retry_date - datetime.datetime.now(retry_date.tzinfo)).total_seconds()
        return max(0, delay)
