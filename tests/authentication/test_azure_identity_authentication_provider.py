from unittest.mock import patch

from azure.identity import EnvironmentCredential
from kiota_abstractions.authentication import AuthenticationProvider

from msgraph_core.authentication import AzureIdentityAuthenticationProvider


def test_subclassing():
    assert issubclass(AzureIdentityAuthenticationProvider, AuthenticationProvider)


def test_is_cae_enabled_is_forwarded_to_kiota_provider():
    with patch(
        "msgraph_core.authentication.azure_identity_authentication_provider."
        "KiotaAzureIdentityAuthenticationProvider.__init__",
        return_value=None,
    ) as init:
        AzureIdentityAuthenticationProvider(EnvironmentCredential(), is_cae_enabled=False)

    assert init.call_args.kwargs["is_cae_enabled"] is False
