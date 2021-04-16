#pylint: disable=invalid-name

from enum import Enum


class APIVersion(str, Enum):
    """Enumerated list of supported API Versions"""
    beta = 'beta'
    v1 = 'v1.0'


class NationalClouds(str, Enum):
    """Enumerated list of supported sovereign clouds"""

    China = 'https://microsoftgraph.chinacloudapi.cn'
    Germany = 'https://graph.microsoft.de'
    Global = 'https://graph.microsoft.com'
    US_DoD = 'https://dod-graph.microsoft.us'
    US_GOV = 'https://graph.microsoft.us'
