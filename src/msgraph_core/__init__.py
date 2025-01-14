# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -----------------------------------

# pylint: disable=line-too-long
# This is to allow complete package description on PyPI
"""
Core component of the Microsoft Graph Python SDK consisting of HTTP/Graph Client and a configurable middleware pipeline (Preview).
"""
from ._constants import SDK_VERSION
from ._enums import APIVersion, NationalClouds
from .authentication import AzureIdentityAuthenticationProvider
from .base_graph_request_adapter import BaseGraphRequestAdapter
from .graph_client_factory import GraphClientFactory
from .models import PageResult
from .tasks import PageIterator

__version__ = SDK_VERSION
