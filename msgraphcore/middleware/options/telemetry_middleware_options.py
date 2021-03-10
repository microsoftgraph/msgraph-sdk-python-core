class TelemetryMiddlewareOptions:
    NONE_FLAG = 0
    REDIRECT_HANDLER_ENABLED_FLAG = 1
    RETRY_HANDLER_ENABLED_FLAG = 2
    AUTH_HANDLER_ENABLED_FLAG = 4
    DEFAULT_HTTPROVIDER_ENABLED_FLAG = 8
    LOGGING_HANDLER_ENABLED_FLAG = 16

    def __init__(self):
        self.feature_usage: int = self.NONE_FLAG
        self.redirect_handler_enabled: int = self.REDIRECT_HANDLER_ENABLED_FLAG
        self.retry_handler_enabled: int = self.RETRY_HANDLER_ENABLED_FLAG
        self.auth_handler_enabled: int = self.AUTH_HANDLER_ENABLED_FLAG
        self.default_http_provider_enabled = self.DEFAULT_HTTPROVIDER_ENABLED_FLAG
        self.logging_handler_enabled: [int] = self.LOGGING_HANDLER_ENABLED_FLAG

    def set_feature_usage(self, flag):
        self.feature_usage = self.feature_usage | flag

    def get_feature_usage(self):
        return hex(self.feature_usage)


telemetry_options = TelemetryMiddlewareOptions()
