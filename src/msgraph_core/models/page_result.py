"""
This module defines the PageResult class which represents a page of
items in a paged response.

The PageResult class provides methods to get and set the next link and
the items in the page, create a PageResult from a discriminator value, set
the value, get the field deserializers, and serialize the PageResult.

Classes:
    PageResult: Represents a page of items in a paged response.
"""
from typing import Any, List, Optional
from __future__ import annotations

from kiota_abstractions.serialization.parsable import Parsable  # type: ignore
from kiota_abstractions.serialization.serialization_writer \
     import SerializationWriter  # type: ignore
from kiota_abstractions.serialization.parse_node import ParseNode  # type: ignore
from typing import TypeVar, List, Optional, Generic

T = TypeVar('T')


class PageResult(Parsable, Generic[T]):
    """
    Represents a page of items in a paged response.
    """
    object_type = None

    def __init__(self, object_type: Optional[Any] = None) -> None:
        PageResult.object_type = object_type
        self._odata_next_link: Optional[str] = None
        self._value: Optional[List[T]] = None

    @property
    def odata_next_link(self) -> Optional[str]:
        """
        Gets the next link for the page.
        Returns:
            Optional[str]: The next link, or None if there is no next link.
        """
        return self._odata_next_link

    @odata_next_link.setter
    def odata_next_link(self, next_link: Optional[str]) -> None:
        """
        Sets the next link for the page.
        Args:
            next_link (Optional[str]): The next link to set.
        """
        self._odata_next_link = next_link

    @property
    def value(self) -> Optional[List[T]]:
        """
        Gets the items in the page.
        Returns:
            Optional[List[Any]]: The items in the page, or None if there
            are no items.
        """
        return self._value

    @value.setter
    def value(self, value: Optional[List[T]]) -> None:
        """
        Sets the items in the page.
        Args:
            value (Optional[List[Any]]): The items to set.
        """
        self._value = value

    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PageResult:  # pylint: disable=unused-argument
        """
        Creates a PageResult from a discriminator value.
        Returns:
            PageResult: The created PageResult.
        """
        impprt_statement = f"from msgraph.generated.models.{str(PageResult.object_type).lower()} \
            import {PageResult.object_type}"

        # pylint: disable=exec-used
        exec(impprt_statement)
        if isinstance(PageResult.object_type, str):
            return PageResult(locals()[PageResult.object_type])
        return PageResult()

    def set_value(self, value: List[Any]):
        """
        Sets the items in the page.

        Args:
            value (List[Any]): The items to set.
        """
        self.value = value

    def get_field_deserializers(self):
        """
        Gets the field deserializers for the PageResult.
        Returns:
            Dict[str, Callable]: The field deserializers.
        """
        class_name = PageResult.object_type
        # pylint: disable=not-callable
        instance = class_name()
        module_path = instance.__class__.__module__
        class_name = instance.__class__.__name__
        import_statement = f'from {module_path} import {class_name}'
        # pylint: disable=exec-used
        exec(import_statement)
        serialization_model = locals()[class_name]
        return {
            '@odata.nextLink':
            lambda parse_node: setattr(self, 'odata_next_link', parse_node.get_str_value()),
            'value':
            lambda parse_node: self.
            set_value(parse_node.get_collection_of_object_values(serialization_model))
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Serializes the PageResult into a SerializationWriter.
        Args:
            writer (SerializationWriter): The writer to serialize into.
        """
        writer.write_str_value('@odata.nextLink', self.odata_next_link, self.value)
        if self.value is not None:
            writer.write_collection_of_object_values('key', 'value', list(self.value))
