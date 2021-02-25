import datetime
from email.utils import parsedate_to_datetime


def get_retry_after(response):
    """
    Check if retry-after is specified in the response header and get the value
    """
    request = response.request
    retry_after = request.headers.get("retry-after")
    if retry_after:
        return parse_retry_after(retry_after)
    for ms_header in ["retry-after-ms", "x-ms-retry-after-ms"]:
        retry_after = request.headers.get(ms_header)
        if retry_after:
            parsed_retry_after = parse_retry_after(retry_after)
            return parsed_retry_after / 1000.0
    return None


def parse_retry_after(retry_after):
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
