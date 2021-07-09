# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import uuid

from .._enums import FeatureUsageFlag


class RequestContext:
    """A request context contains data that is persisted throughout the request and
    includes a ClientRequestId property, MiddlewareControl property to control behavior
    of middleware as well as a FeatureUsage  property to keep track of middleware used
    in making the request.
    """
    def __init__(self, middleware_control, headers):
        """Constructor for request context instances

        Args:
            middleware_control (dict): A dictionary of optional middleware options
            that can be accessed by middleware components to override the options provided
            during middleware initialization,

            headers (dict): A dictionary containing the request headers. Used to check for a
            user provided client request id.
        """
        self.middleware_control = middleware_control
        self.client_request_id = headers.get('client-request-id', str(uuid.uuid4()))
        self._feature_usage = FeatureUsageFlag.NONE

    @property
    def feature_usage(self):
        return hex(self._feature_usage)

    @feature_usage.setter
    def set_feature_usage(self, flag: FeatureUsageFlag):
        self._feature_usage = self._feature_usage | flag
