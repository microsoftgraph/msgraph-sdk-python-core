# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.identity import EnvironmentCredential
from requests import Session

from msgraph.core import APIVersion, HTTPClientFactory
from msgraph.core.middleware.authorization import AuthorizationHandler


def test_client_factory_with_default_middleware():
    """
    Test that a client created from client factory with default middleware
    works as expected.
    """
    credential = EnvironmentCredential()
    client = HTTPClientFactory().create_with_default_middleware(credential)
    response = client.get('https://graph.microsoft.com/v1.0/users')
    assert response.status_code == 200


def test_client_factory_with_user_provided_session():
    """
    Test that the client works with a user provided session object
    """

    session = Session()
    credential = EnvironmentCredential()
    client = HTTPClientFactory(session=session).create_with_default_middleware(credential)
    response = client.get('https://graph.microsoft.com/v1.0/users')
    assert response.status_code == 200


def test_client_factory_with_custom_settings():
    """
    Test that the client works with user provided configuration
    """
    credential = EnvironmentCredential()
    client = HTTPClientFactory(api_version=APIVersion.beta
                               ).create_with_default_middleware(credential)
    response = client.get('https://graph.microsoft.com/v1.0/users')
    assert response.status_code == 200


def test_client_factory_with_custom_middleware():
    """
    Test client factory works with user provided middleware
    """
    credential = EnvironmentCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = HTTPClientFactory().create_with_custom_middleware(middleware)
    response = client.get('https://graph.microsoft.com/v1.0/users')
    assert response.status_code == 200


def test_context_object_is_attached_to_requests_from_client_factory():
    """
    Test that requests from a native HTTP client have a context object attached
    """
    credential = EnvironmentCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = HTTPClientFactory().create_with_custom_middleware(middleware)
    response = client.get('https://graph.microsoft.com/v1.0/users')
    assert response.status_code == 200
    assert hasattr(response.request, 'context')


def test_middleware_control_is_empty_for_requests_from_client_factory():
    """
    Test that requests from a native HTTP client have no middlware options in the middleware
    control
    """
    credential = EnvironmentCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = HTTPClientFactory().create_with_custom_middleware(middleware)
    response = client.get('https://graph.microsoft.com/v1.0/users')
    assert response.status_code == 200
    assert response.request.context.middleware_control == {}
