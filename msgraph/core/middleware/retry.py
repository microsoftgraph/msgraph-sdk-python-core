import time

import httpx
from kiota_http.middleware import RetryHandler

from .._enums import FeatureUsageFlag
from .middleware import GraphRequest


class GraphRetryHandler(RetryHandler):
    """
    Middleware that handles failed requests
    """

    async def send(self, request: GraphRequest, transport: httpx.AsyncBaseTransport):
        """
        Sends the http request object to the next middleware or retries the request if necessary.
        """
        response = None
        retry_count = 0
        retry_valid = self.retries_allowed

        request.context.feature_usage = FeatureUsageFlag.RETRY_HANDLER_ENABLED

        while retry_valid:
            start_time = time.time()
            if retry_count > 0:
                request.headers.update({'retry-attempt': f'{retry_count}'})
            response = await super().send(request, transport)
            # Check if the request needs to be retried based on the response method
            # and status code
            if self.should_retry(request, response):
                # check that max retries has not been hit
                retry_valid = self.check_retry_valid(retry_count)

                # Get the delay time between retries
                delay = self.get_delay_time(retry_count, response)

                if retry_valid and delay < self.timeout:
                    time.sleep(delay)
                    end_time = time.time()
                    self.timeout -= (end_time - start_time)
                    # increment the count for retries
                    retry_count += 1

                    continue
            break
        return response
