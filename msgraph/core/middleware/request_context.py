# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import uuid

from .._enums import FeatureUsageFlag


class RequestContext:
    def __init__(self, middleware_control, headers):
        self.middleware_control = middleware_control
        self.client_request_id = headers.get('client-request-id', str(uuid.uuid4()))
        self._feature_usage = FeatureUsageFlag.NONE

    @property
    def feature_usage(self):
        return hex(self._feature_usage)

    @feature_usage.setter
    def set_feature_usage(self, flag: FeatureUsageFlag):
        self._feature_usage = self._feature_usage | flag
