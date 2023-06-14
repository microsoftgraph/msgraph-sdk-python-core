from azure.identity import EnvironmentCredential
from kiota_abstractions.authentication import AuthenticationProvider

from msgraph_core.authentication import AzureIdentityAuthenticationProvider


def test_subclassing():
    assert issubclass(AzureIdentityAuthenticationProvider, AuthenticationProvider)


def test_create_provider():
    credential = EnvironmentCredential()
    auth_provider = AzureIdentityAuthenticationProvider(credential)

    allowed_hosts = auth_provider.__dict__.get('allowed_hosts', None)
    assert allowed_hosts is not None
    assert 'https://graph.microsoft.com' in allowed_hosts

    scopes = auth_provider.__dict__.get('scopes', None)
    assert scopes is not None
    assert 'https://graph.microsoft.com/.default' in scopes
