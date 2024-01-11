from typing import TYPE_CHECKING, Dict, List, Optional, Union

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
        options: Optional[Dict] = {},
        scopes: List[str] = [],
        allowed_hosts: Optional[List[str]] = [nc.value for nc in NationalClouds]
    ) -> None:
        """[summary]

        Args:
            credentials (Union["TokenCredential", "AsyncTokenCredential"]): The
                tokenCredential implementation to use for authentication.
            options (Optional[dict]): The options to use for authentication.
            scopes (List[str]): The scopes to use for authentication.
                Defaults to 'https://<national_cloud_domain>/.default'.
            allowed_hosts (Optional[List[str]]): The allowed hosts to use for
                authentication. Defaults to Microsoft National Clouds.
        """
        super().__init__(credentials, options, scopes, allowed_hosts)
