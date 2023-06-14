from typing import TYPE_CHECKING, List, Union, Optional, Dict

from kiota_authentication_azure.azure_identity_authentication_provider import \
    AzureIdentityAuthenticationProvider as KiotaAzureIdentityAuthenticationProvider
from msgraph_core._constants import MS_DEFAULT_SCOPE
from msgraph_core._enums import NationalClouds

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential


class AzureIdentityAuthenticationProvider(KiotaAzureIdentityAuthenticationProvider):

    def __init__(
        self,
        credentials: Union["TokenCredential", "AsyncTokenCredential"],
        options: Optional[Dict] = None,
        scopes: Optional[List[str]] = None,
        allowed_hosts: Optional[List[str]] = None
    ) -> None:
        """[summary]

        Args:
            credentials (Union["TokenCredential", "AsyncTokenCredential"]): The
                tokenCredential implementation to use for authentication.
            options (Optional[dict]): The options to use for authentication.
            scopes (List[str], optional): The scopes to use for authentication.
                Defaults to 'https://graph.microsoft.com/.default'.
            allowed_hosts (Set[str], optional): The allowed hosts to use for
                authentication. Defaults to Microsoft National Clouds.
        """
        self.scopes: List[str] = [MS_DEFAULT_SCOPE] if scopes is None else scopes
        self.allowed_hosts: List[str] = [nc.value
                                         for nc in NationalClouds] if allowed_hosts is None else []
        super().__init__(credentials, options, self.scopes, self.allowed_hosts)
