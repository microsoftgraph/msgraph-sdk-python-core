from msgraph_core.models import PageResult  # pylint: disable=no-name-in-module, import-error


def test_initialization():
    page_result = PageResult()
    assert page_result.odata_next_link is None
    assert page_result.value is None


def test_set_and_get_values():
    page_result = PageResult()
    page_result.value = [{"name": "John Doe"}, {"name": "Ian Smith"}]
    page_result.odata_next_link = "next_page"
    assert 2 == len(page_result.value)
    assert "next_page" == page_result.odata_next_link
    assert [{"name": "John Doe"}, {"name": "Ian Smith"}] == page_result.value
