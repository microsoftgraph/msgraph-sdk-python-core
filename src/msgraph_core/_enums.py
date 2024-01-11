# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=invalid-name

from enum import Enum


class APIVersion(str, Enum):
    """Enumerated list of supported API Versions"""
    beta = 'beta'
    v1 = 'v1.0'


class FeatureUsageFlag(int, Enum):
    """Enumerated list of values used to flag usage of specific middleware"""

    NONE = 0
    REDIRECT_HANDLER_ENABLED = 1
    RETRY_HANDLER_ENABLED = 2
    AUTH_HANDLER_ENABLED = 4
    DEFAULT_HTTP_PROVIDER_ENABLED = 8
    LOGGING_HANDLER_ENABLED = 16


class NationalClouds(str, Enum):
    """Enumerated list of supported sovereign clouds"""

    China = 'https://microsoftgraph.chinacloudapi.cn'
    Germany = 'https://graph.microsoft.de'
    Global = 'https://graph.microsoft.com'
    US_DoD = 'https://dod-graph.microsoft.us'
    US_GOV = 'https://graph.microsoft.us'
