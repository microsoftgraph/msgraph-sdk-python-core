import uuid

from msgraphcore.enums import FeatureUsageFlag
from msgraphcore.middleware.options.middleware_control import middleware_control


class RequestContext:
    def __init__(self, request):
        self.middleware_control = middleware_control
        self.client_request_id = request.headers.get('client-request-id', str(uuid.uuid4()))
        self._feature_usage = FeatureUsageFlag.NONE

    @property
    def feature_usage(self):
        return hex(self._feature_usage)

    @feature_usage.setter
    def set_feature_usage(self, flag: FeatureUsageFlag):
        self._feature_usage = self.feature_usage | flag
