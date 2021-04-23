import uuid

from msgraphcore.middleware.options.middleware_control import middleware_control


class RequestContext:
    NONE_FLAG = 0
    REDIRECT_HANDLER_ENABLED_FLAG = 1
    RETRY_HANDLER_ENABLED_FLAG = 2
    AUTH_HANDLER_ENABLED_FLAG = 4
    DEFAULT_HTTPROVIDER_ENABLED_FLAG = 8
    LOGGING_HANDLER_ENABLED_FLAG = 10

    def __init__(self, request):
        self.middleware_control = middleware_control
        self.client_request_id = request.headers.get('client-request-id', str(uuid.uuid4()))
        self._feature_usage = self.NONE_FLAG

    @property
    def feature_usage(self):
        return hex(self._feature_usage)

    @feature_usage.setter
    def set_feature_usage(self, flag):
        self._feature_usage = self.feature_usage | flag
