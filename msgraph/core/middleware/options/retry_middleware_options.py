class RetryMiddlewareOptions:
    def __init__(self, retry_configs):
        self.retry_total: int = retry_configs.get('retry_total')
        self.retry_backoff_factor: int = retry_configs.get('retry_backoff_factor')
        self.retry_backoff_max: int = retry_configs.get('retry_backoff_max')
        self.retry_time_limit: int = retry_configs.get('retry_time_limit')
        self.retry_on_status_codes: [int] = retry_configs.get('retry_on_status_codes')
