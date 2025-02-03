"""
This module defines the PageResult class which represents a page of
items in a paged response.

The PageResult class provides methods to get and set the next link and
the items in the page, create a PageResult from a discriminator value, set
the value, get the field deserializers, and serialize the PageResult.

Classes:
    PageResult: Represents a page of items in a paged response.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional, TypeVar

from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.serialization.parse_node import ParseNode
from kiota_abstractions.serialization.serialization_writer import SerializationWriter

T = TypeVar('T')


@dataclass
class PageResult(Parsable):
    odata_next_link: Optional[str] = None
    value: Optional[list[Parsable]] = None

    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> PageResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Attachment
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null")
        return PageResult()

    def get_field_deserializers(self) -> dict[str, Callable[[ParseNode], None]]:
        """Gets the deserialization information for this object.

        Returns:
            dict[str, Callable[[ParseNode], None]]: The deserialization information for this
            object where each entry is a property key with its deserialization callback.
        """
        return {
            "@odata.nextLink":
            lambda x: setattr(self, "odata_next_link", x.get_str_value()),
            "value":
            lambda x: setattr(
                self,
                "value",
                x.get_collection_of_object_values(
                    Parsable  # type: ignore
                    # Bug. Should get a collection of primitive dictionary objects
                )
            )
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """Writes the objects properties to the current writer.

        Args:
            writer (SerializationWriter): The writer to write to.
        """
        if not writer:
            raise TypeError("Writer cannot be null")
        writer.write_str_value("@odata.nextLink", self.odata_next_link)
        writer.write_collection_of_object_values("value", self.value)
