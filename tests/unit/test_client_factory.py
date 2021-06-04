# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from requests import Session
from requests.adapters import HTTPAdapter

from msgraph.core import APIVersion, HTTPClientFactory, NationalClouds
from msgraph.core._constants import CONNECTION_TIMEOUT, REQUEST_TIMEOUT
from msgraph.core.middleware.authorization import AuthorizationHandler


def test_initialize_with_default_config():
    """Test creation of HTTP Client will use the default configuration
    if none are passed"""
    client = HTTPClientFactory()

    assert client.api_version == APIVersion.v1
    assert client.endpoint == NationalClouds.Global
    assert client.timeout == (CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
    assert isinstance(client.session, Session)


def test_initialize_with_custom_config():
    """Test creation of HTTP Client will use custom configuration if they are passed"""
    client = HTTPClientFactory(api_version=APIVersion.beta, timeout=(5, 5))

    assert client.api_version == APIVersion.beta
    assert client.endpoint == NationalClouds.Global
    assert client.timeout == (5, 5)
    assert isinstance(client.session, Session)


def test_create_with_default_middleware():
    """Test creation of HTTP Client using default middleware"""
    credential = _CustomTokenCredential()
    client = HTTPClientFactory().create_with_default_middleware(credential=credential)
    middleware = client.get_adapter('https://')

    assert isinstance(middleware, HTTPAdapter)


def test_create_with_custom_middleware():
    """Test creation of HTTP Clients with custom middleware"""
    credential = _CustomTokenCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = HTTPClientFactory().create_with_custom_middleware(middleware=middleware)
    custom_middleware = client.get_adapter('https://')

    assert isinstance(custom_middleware, HTTPAdapter)


def test_get_base_url():
    """
    Test base url is formed by combining the national cloud endpoint with
    Api version
    """
    client = HTTPClientFactory(api_version=APIVersion.beta, cloud=NationalClouds.Germany)
    assert client.session.base_url == client.endpoint + '/' + client.api_version


def test_register_middleware():
    credential = _CustomTokenCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = HTTPClientFactory()
    client._register(middleware)

    assert isinstance(client.session.get_adapter('https://'), HTTPAdapter)


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']
