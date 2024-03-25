from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from kiota_abstractions.serialization.additional_data_holder import AdditionalDataHolder
from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.serialization.parse_node import ParseNode
from kiota_abstractions.serialization.serialization_writer import SerializationWriter


@dataclass
class LargeFileUploadSession:
    upload_url: Optional[str] = None
    expiration_date_time: Optional[datetime] = None
    additional_data: List[Dict[str, any]] = field(default_factory=list)
    is_cancelled: Optional[bool] = False
    next_expected_ranges: Optional[List[str]] = field(default_factory=list)

    @staticmethod
    def create_from_discriminator_value(
        parse_node: ParseNode
    ) -> Optional['LargeFileUploadSession']:
        return LargeFileUploadSession()

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_str_value('upload_url', self.upload_url)
        writer.write_datetime_value('expiration_date_time', self.expiration_date_time)
        writer.write_bool_value('is_cancelled', self.is_cancelled)
        writer.write_collection_of_primitive_values(
            'next_expected_ranges', self.next_expected_ranges
        )
        writer.write_additional_data_value(self.additional_data)

    def get_field_deserializers(self) -> Dict[str, any]:
        return {
            'upload_url':
            lambda parse_node: setattr(self, 'upload_url', parse_node.get_string_value()),
            'expiration_date_time':
            lambda parse_node:
            setattr(self, 'expiration_date_time', parse_node.get_date_time_value()),
            'is_cancelled':
            lambda parse_node: setattr(self, 'is_cancelled', parse_node.get_boolean_value()),
            'next_expected_ranges':
            lambda parse_node: setattr(
                self, 'next_expected_ranges', parse_node.
                get_collection_of_primitive_values('string')
            )
        }
