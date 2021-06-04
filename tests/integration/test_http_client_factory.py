import pytest
from requests import Session

from msgraph.core.client_factory import HTTPClientFactory
from msgraph.core.enums import APIVersion
from msgraph.core.middleware.authorization import AuthorizationHandler


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']


def test_client_factory_with_default_middleware():
    """
    Test that a client created from client factory with default middleware
    works as expected.
    """
    credential = _CustomTokenCredential()
    client = HTTPClientFactory().create_with_default_middleware(credential)
    response = client.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    assert response.status_code == 200


def test_client_factory_with_user_provided_session():
    """
    Test that the client works with a user provided session object
    """

    session = Session()
    credential = _CustomTokenCredential()
    client = HTTPClientFactory(session=session).create_with_default_middleware(credential)
    response = client.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    assert response.status_code == 200


def test_client_factory_with_custom_settings():
    """
    Test that the client works with user provided configuration
    """
    credential = _CustomTokenCredential()
    client = HTTPClientFactory(api_version=APIVersion.beta
                               ).create_with_default_middleware(credential)
    response = client.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    assert response.status_code == 200


def test_client_factory_with_custom_middleware():
    """
    Test client factory works with user provided middleware
    """
    credential = _CustomTokenCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = HTTPClientFactory().create_with_custom_middleware(middleware)
    response = client.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    assert response.status_code == 200


def test_context_object_is_attached_to_requests_from_client_factory():
    """
    Test that requests from a native HTTP client have a context object attached
    """
    credential = _CustomTokenCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = HTTPClientFactory().create_with_custom_middleware(middleware)
    response = client.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    assert response.status_code == 200
    assert hasattr(response.request, 'context')


def test_middleware_control_is_empty_for_requests_from_client_factory():
    """
    Test that requests from a native HTTP client have no middlware options in the middleware
    control
    """
    credential = _CustomTokenCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = HTTPClientFactory().create_with_custom_middleware(middleware)
    response = client.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    assert response.status_code == 200
    assert response.request.context.middleware_control == {}
