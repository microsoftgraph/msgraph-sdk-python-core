import os
from unittest.mock import AsyncMock, patch, Mock

import pytest
from azure.identity import ClientSecretCredential
from kiota_authentication_azure.azure_identity_authentication_provider\
     import AzureIdentityAuthenticationProvider
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from dotenv import load_dotenv

from msgraph_core.tasks.page_iterator import PageIterator  # pylint: disable=import-error, no-name-in-module
from msgraph_core.models.page_result import PageResult  # pylint: disable=no-name-in-module, import-error


@pytest.fixture
def first_page_data():
    return {
        "@odata.context":
        "https://graph.microsoft.com/v1.0/$metadata#users",
        "@odata.next_link":
        "https://graph.microsoft.com/v1.0/users?skip=2&page=10",
        "value": [
            {
                "businessPhones": [],
                "displayName": "Conf Room Adams 1",
                "givenName": None,
                "jobTitle": None,
                "mail": "Adams@contoso.com",
                "mobilePhone": None,
                "officeLocation": None,
                "preferredLanguage": None,
                "surname": None,
                "userPrincipalName": "Adams@contoso.com",
                "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
            }, {
                "businessPhones": ["425-555-0100"],
                "displayName": "MOD Administrator 1",
                "givenName": "MOD",
                "jobTitle": None,
                "mail": None,
                "mobilePhone": "425-555-0101",
                "officeLocation": None,
                "preferredLanguage": "en-US",
                "surname": "Administrator",
                "userPrincipalName": "admin@contoso.com",
                "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
            }
        ]
    }


@pytest.fixture
def second_page_data():
    return {
        "@odata.context":
        "https://graph.microsoft.com/v1.0/$metadata#users",
        "value": [
            {
                "businessPhones": [],
                "displayName": "Conf Room Adams 2",
                "givenName": None,
                "jobTitle": None,
                "mail": "Adams@contoso.com",
                "mobilePhone": None,
                "officeLocation": None,
                "preferredLanguage": None,
                "surname": None,
                "userPrincipalName": "Adams@contoso.com",
                "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
            }, {
                "businessPhones": ["425-555-0100"],
                "displayName": "MOD Administrator 2",
                "givenName": "MOD",
                "jobTitle": None,
                "mail": None,
                "mobilePhone": "425-555-0101",
                "officeLocation": None,
                "preferredLanguage": "en-US",
                "surname": "Administrator",
                "userPrincipalName": "admin@contoso.com",
                "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
            }
        ]
    }


credential = Mock()
auth_provider = Mock()
request_adapter = Mock()


def test_convert_to_page(first_page_data):  # pylint: disable=redefined-outer-name

    page_iterator = PageIterator(first_page_data, request_adapter)
    first_page = page_iterator.convert_to_page(first_page_data)
    first_page.value = first_page_data['value']
    first_page.odata_next_link = first_page_data['@odata.next_link']
    assert isinstance(first_page, PageResult)
    assert first_page_data['value'] == first_page.value
    assert first_page_data['@odata.next_link'] == first_page.odata_next_link


@pytest.mark.asyncio
async def test_iterate():
    # Mock the next method to return None after the first call
    with patch.object(PageIterator, 'next', new_callable=AsyncMock) as mock_next:
        mock_next.side_effect = [True, None]

        with patch.object(PageIterator, 'enumerate', return_value=True) as mock_enumerate:
            page_iterator = PageIterator(first_page_data, request_adapter)
            await page_iterator.iterate(lambda _: True)
            assert mock_next.call_count == 2
            assert mock_enumerate.call_count == 2
