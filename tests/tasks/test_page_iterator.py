import pytest

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_serialization_json import JsonNodeFactory
from kiota_serialization_json import JsonParseNode
from kiota_http_python.exceptions import KiotaHTTPXError
from ...src.msgraph_core.page_iterator import PageIterator

@pytest.fixture
def first_page_data():
    return {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
        "@odata.nextLink": "https://graph.microsoft.com/v1.0/users?skip=2&page=10",
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
            },
            {
                "businessPhones": [
                    "425-555-0100"
                ],
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
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
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
            },
            {
                "businessPhones": [
                    "425-555-0100"
                ],
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

def test_handler_can_work(first_page_data, second_page_data):
    with requests_mock.Mocker() as m:
        m.get('https://graph.microsoft.com/v1.0/users', json=first_page_data)
        m.get('https://graph.microsoft.com/v1.0/users?skip=2&page=10', json=second_page_data)

        page_iterator = PageIterator(first_page_data, RequestAdapter())
        count = 0
        page_iterator.iterate(lambda _: count + 1) 
        assert count == 4