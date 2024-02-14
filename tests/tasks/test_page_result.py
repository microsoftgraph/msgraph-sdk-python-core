import pytest

from kiota_serialization_json import JsonSerializationWriter

from msgraph_core.models import PageResult


def test_set_and_get_values():
    page_result = PageResult()
    writer = JsonSerializationWriter()
    writer.get_serialized_content(page_result)
    page_result.set_value([{"name": "John Doe"}, {"name": "Ian Smith"}])
    page_result.odata_next_link = "next_page"
    assert 2 == len(page_result.value)
    assert "next_page" == page_result.odata_next_link
    assert {
        "@odata.nextLink": "next_page",
        "value": [{
            "name": "John Doe"
        }, {
            "name": "Ian Smith"
        }]
    } == writer.get_serialized_content(page_result)
