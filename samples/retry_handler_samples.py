# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
"""Demonstrates using the GraphClient to make HTTP Requests to Microsoft Graph"""
import json
from pprint import pprint

from azure.identity import InteractiveBrowserCredential

from msgraph.core import GraphClient, HTTPClientFactory

scopes = ['user.read']
# This sample uses InteractiveBrowserCredential only for demonstration.
# Any azure-identity TokenCredential class will work the same.
browser_credential = InteractiveBrowserCredential(client_id='YOUR_CLIENT_ID')


def sample_http_client_with_custom_retry_defaults():
    """
    Initializing a sample client with default middleware using the HTTPClientand passing
    default configs to the retryhandler. These defaults will be used for every subsequent
    request using the client."""

    client = HTTPClientFactory().create_with_default_middleware(
        browser_credential, retry_total=5, retry_backoff_factor=0.1, retry_time_limit=60
    )
    result = client.get('/me/messages', scopes=['mail.read'])
    pprint(result.json())


def sample_graph_client_with_custom_retry_defaults():
    """Initializing a sample graph client and passing default configs to the default retry
    handler. These defaults will be used for every subsequent request using the client unless
    per request options are passed"""

    client = GraphClient(credential=browser_credential, retry_total=2, retry_backoff_factor=0.5)
    result = client.get('/me/messages', scopes=['mail.read'])
    pprint(result.json())


def sample_graph_client_with_per_request_retry_options():
    """Sending a request using the graph client with retry options for that specific request.
    This will override the default config for the retry handler"""

    client = GraphClient(credential=browser_credential)
    result = client.get(
        '/me/messages', scopes=['mail.read'], retry_on_status_codes=[429, 502, 503, 504]
    )
    pprint(result.json())
