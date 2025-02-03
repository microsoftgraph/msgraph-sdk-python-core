from __future__ import annotations

import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Optional

from kiota_abstractions.serialization import (
    AdditionalDataHolder,
    Parsable,
    ParseNode,
    SerializationWriter,
)


@dataclass
class LargeFileUploadSession(AdditionalDataHolder, Parsable):

    additional_data: dict[str, Any] = field(default_factory=dict)
    expiration_date_time: Optional[datetime.datetime] = None
    next_expected_ranges: Optional[list[str]] = None
    is_cancelled: Optional[bool] = False
    odata_type: Optional[str] = None
    # The URL endpoint that accepts PUT requests for byte ranges of the file.
    upload_url: Optional[str] = None

    @staticmethod
    def create_from_discriminator_value(
        parse_node: Optional[ParseNode] = None
    ) -> LargeFileUploadSession:
        """
        Creates a new instance of the appropriate class based
        on discriminator value param parse_node: The parse node
        to use to read the discriminator value and create the object
        Returns: UploadSession
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null.")
        return LargeFileUploadSession()

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
