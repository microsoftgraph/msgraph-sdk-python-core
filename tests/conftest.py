import httpx
import pytest
from azure.identity.aio import DefaultAzureCredential
from kiota_abstractions.authentication import AccessTokenProvider
from kiota_authentication_azure.azure_identity_access_token_provider import (
    AzureIdentityAccessTokenProvider,
)

from msgraph.core import APIVersion, NationalClouds
from msgraph.core.middleware import GraphRequest, GraphRequestContext

BASE_URL = NationalClouds.Global + '/' + APIVersion.v1


class MockAccessTokenProvider(AccessTokenProvider):

    async def get_authorization_token(self, request: GraphRequest) -> str:
        """Returns a string representing a dummy token
        Args:
            request (GraphRequest): Graph request object
        """
        return "Sample token"

    def get_allowed_hosts_validator(self) -> None:
        pass


@pytest.fixture
def mock_token_provider():
    return MockAccessTokenProvider()


@pytest.fixture
def mock_transport():
    return httpx.AsyncClient()._transport


@pytest.fixture
def mock_request():
    req = httpx.Request('GET', "https://example.org")
    req.context = GraphRequestContext({}, req.headers)
    return req


@pytest.fixture
def mock_graph_request():
    req = httpx.Request('GET', BASE_URL)
    req.context = GraphRequestContext({}, req.headers)
    return req


@pytest.fixture
def mock_response():
    return httpx.Response(
        json={'message': 'Success!'}, status_code=200, headers={"Content-Type": "application/json"}
    )
