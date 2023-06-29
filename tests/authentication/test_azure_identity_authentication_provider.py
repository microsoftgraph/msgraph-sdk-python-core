from azure.identity import EnvironmentCredential
from kiota_abstractions.authentication import AuthenticationProvider

from msgraph_core.authentication import AzureIdentityAuthenticationProvider


def test_subclassing():
    assert issubclass(AzureIdentityAuthenticationProvider, AuthenticationProvider)
