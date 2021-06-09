import datetime
import random
import sys
import time
from email.utils import parsedate_to_datetime

from msgraph.core.middleware.middleware import BaseMiddleware


class RetryHandler(BaseMiddleware):
    """
    TransportAdapter that allows us to specify the
    retry policy for all requests
    """

    DEFAULT_MAX_RETRIES = 3
    MAX_RETRIES = 10
    DEFAULT_DELAY = 3
    MAX_DELAY = 180
    DEFAULT_BACKOFF_FACTOR = 0.5
    MAXIMUM_BACKOFF = 120
    _DEFAULT_RETRY_STATUS_CODES = {429, 503, 504}

    def __init__(self, **kwargs):
        super().__init__()
        self.max_retries: int = min(
            kwargs.pop('max_retries', self.DEFAULT_MAX_RETRIES), self.MAX_RETRIES
        )
        self.backoff_factor: float = kwargs.pop('retry_backoff_factor', self.DEFAULT_BACKOFF_FACTOR)
        self.backoff_max: int = kwargs.pop('retry_backoff_max', self.MAXIMUM_BACKOFF)
        self.timeout: int = kwargs.pop('retry_time_limit', self.MAX_DELAY)

        status_codes: [int] = kwargs.pop('retry_on_status_codes', [])

        self._retry_on_status_codes: set = set(status_codes) | self._DEFAULT_RETRY_STATUS_CODES
        self._allowed_methods: set = frozenset(
            ['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
        )
        self._respect_retry_after_header: bool = True

    @classmethod
    def disable_retries(cls):
        """
        Disable retries by setting retry_total to zero.
        retry_total takes precedence over all other counts.
        """
        return cls(max_retries=0)

    def get_retry_options(self, middleware_control):
        """
        Check if request specific configs have been passed and override any session defaults
        Then configure retry settings into the form of a dict.
        """
        if middleware_control:
            return {
                'total':
                min(middleware_control.get('max_retries', self.max_retries), self.MAX_RETRIES),
                'backoff':
                middleware_control.get('retry_backoff_factor', self.backoff_factor),
                'max_backoff':
                middleware_control.get('retry_backoff_max', self.backoff_max),
                'timeout':
                middleware_control.get('retry_time_limit', self.timeout),
                'retry_codes':
                set(middleware_control.get('retry_on_status_codes', self._retry_on_status_codes))
                | set(self._DEFAULT_RETRY_STATUS_CODES),
                'methods':
                self._allowed_methods,
            }
        return {
            'total': self.max_retries,
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
        retry_options = self.get_retry_options(request.context.middleware_control)
        absolute_time_limit = min(retry_options['timeout'], self.MAX_DELAY)
        response = None
        retry_count = 0
        retry_valid = True

        while retry_valid:
            try:
                start_time = time.time()
                request.headers.update({'retry-attempt': '{}'.format(retry_count)})
                response = super().send(request, **kwargs)
                # Check if the request needs to be retried based on the response method
                # and status code
                if self.should_retry(retry_options, response):
                    # check that max retries has not been hit
                    retry_valid = self.check_retry_valid(retry_options, retry_count)

                    # Get the delay time between retries
                    delay = self.get_delay_time(retry_options, retry_count, response)

                    if retry_valid and delay < absolute_time_limit:
                        time.sleep(delay)
                        end_time = time.time()
                        absolute_time_limit -= (end_time - start_time)
                        # increment the count for retries
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

    def check_retry_valid(self, retry_options, retry_count):
        """
        Check that the max retries limit has not been hit
        """
        if retry_count < retry_options['total']:
            return True
        return False

    def get_delay_time(self, retry_options, retry_count, response=None):
        """
        Get the time in seconds to delay between retry attempts.
        Respects a retry-after header in the response if provided
        If no retry-after response header, it defaults to exponential backoff
        """
        retry_after = self._get_retry_after(response)
        if retry_after:
            return retry_after
        return self._get_delay_time_exp_backoff(retry_options, retry_count)

    def _get_delay_time_exp_backoff(self, retry_options, retry_count):
        """
        Get time in seconds to delay between retry attempts based on an exponential
        backoff value.
        """
        exp_backoff_value = retry_options['backoff'] * +(2**(retry_count - 1))
        backoff_value = exp_backoff_value + (random.randint(0, 1000) / 1000)

        backoff = min(retry_options['max_backoff'], backoff_value)
        return backoff

    def _get_retry_after(self, response):
        """
        Check if retry-after is specified in the response header and get the value
        """
        retry_after = response.headers.get("retry-after")
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
