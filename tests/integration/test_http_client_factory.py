import pytest
from requests import Session

from msgraphcore.client_factory import HTTPClientFactory
from msgraphcore.enums import APIVersion
from msgraphcore.middleware.authorization import AuthorizationHandler


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
