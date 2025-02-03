from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from kiota_abstractions.serialization import (
    AdditionalDataHolder,
    Parsable,
    ParseNode,
    SerializationWriter,
)

T = TypeVar('T')


@dataclass
class UploadSessionDataHolder(AdditionalDataHolder, Parsable):
    expiration_date_time: Optional[datetime] = None
    next_expected_ranges: Optional[list[str]] = None
    upload_url: Optional[str] = None
    odata_type: Optional[str] = None

    def get_field_deserializers(self, ) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "expirationDateTime":
            lambda n: setattr(self, 'expiration_date_time', n.get_datetime_value()),
            "nextExpectedRanges":
            lambda n:
            setattr(self, 'next_expected_ranges', n.get_collection_of_primitive_values(str)),
            "@odata.type":
            lambda n: setattr(self, 'odata_type', n.get_str_value()),
            "uploadUrl":
            lambda n: setattr(self, 'upload_url', n.get_str_value()),
        }
        return fields

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if not writer:
            raise TypeError("writer cannot be null.")
        writer.write_datetime_value("expirationDateTime", self.expiration_date_time)
        writer.write_collection_of_primitive_values("nextExpectedRanges", self.next_expected_ranges)
        writer.write_str_value("@odata.type", self.odata_type)
        writer.write_str_value("uploadUrl", self.upload_url)
        writer.write_additional_data_value(self.additional_data)


class UploadResult(Generic[T]):

    def __init__(self) -> None:
        self.upload_session: Optional[UploadSessionDataHolder] = None
        self.item_response: Optional[T] = None
        self.location: Optional[str] = None

    @property
    def upload_succeeded(self) -> bool:
        return self.item_response is not None or self.location is not None
