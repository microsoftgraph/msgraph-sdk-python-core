from typing import TYPE_CHECKING, Optional, Union

from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider as KiotaAzureIdentityAuthenticationProvider,
)

from msgraph_core._constants import MS_DEFAULT_SCOPE
from msgraph_core._enums import NationalClouds

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential


class AzureIdentityAuthenticationProvider(KiotaAzureIdentityAuthenticationProvider):

    def __init__(
        self,
        credentials: Union["TokenCredential", "AsyncTokenCredential"],
        options: Optional[dict] = {},
        scopes: list[str] = [],
        allowed_hosts: list[str] = [nc.value for nc in NationalClouds],
        is_cae_enabled: bool = True,
    ) -> None:
        """[summary]

        Args:
            credentials (Union["TokenCredential", "AsyncTokenCredential"]): The
                tokenCredential implementation to use for authentication.
            options (Optional[dict]): The options to use for authentication.
            scopes (list[str]): The scopes to use for authentication.
                Defaults to 'https://<national_cloud_domain>/.default'.
            allowed_hosts (Optional[list[str]]): The allowed hosts to use for
                authentication. Defaults to Microsoft National Clouds.
            is_cae_enabled (bool): Whether Continuous Access Evaluation is
                enabled for the authentication provider. Defaults to True.
        """
        super().__init__(credentials, options, scopes, allowed_hosts, is_cae_enabled=is_cae_enabled)
