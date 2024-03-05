from typing import List, Dict, Optional
from datetime import datetime

from kiota_abstractions.serialization.additional_data_holder import AdditionalDataHolder
from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.serialization.parse_node import ParseNode
from kiota_abstractions.serialization.serialization_writer import SerializationWriter


class LargeFileUploadSession(Parsable, AdditionalDataHolder):

    def __init__(self):
        self.upload_url: Optional[str] = None
        self.expiration_date_time: Optional[datetime] = None
        self.additional_data: Dict[str, any] = {}
        self.is_cancelled: Optional[bool] = False
        self.next_expected_ranges: Optional[List[str]] = None

    def set_expiration_date_time(self, expiration_date_time: Optional[datetime]):
        self.expiration_date_time = expiration_date_time

    def set_upload_url(self, upload_url: Optional[str]):
        self.upload_url = upload_url

    def set_next_expected_ranges(self, next_expected_ranges: Optional[List[str]]):
        self.next_expected_ranges = next_expected_ranges

    def get_next_expected_ranges(self) -> Optional[List[str]]:
        return self.next_expected_ranges

    def get_expiration_date_time(self) -> Optional[datetime]:
        return self.expiration_date_time

    def get_upload_url(self) -> Optional[str]:
        return self.upload_url

    def set_is_cancelled(self, is_cancelled: Optional[bool]):
        self.is_cancelled = is_cancelled

    def get_additional_data(self) -> Optional[Dict[str, any]]:
        return self.additional_data

    def set_additional_data(self, value: Dict[str, any]):
        self.additional_data = value

    @staticmethod
    def create_from_discriminator_value(
        parse_node: ParseNode
    ) -> Optional['LargeFileUploadSession']:
        return LargeFileUploadSession()

    def get_is_cancelled(self) -> Optional[bool]:
        return self.is_cancelled

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_string_value('uploadUrl', self.upload_url)
        writer.write_date_time_value('expirationDateTime', self.expiration_date_time)
        writer.write_boolean_value('isCancelled', self.is_cancelled)
        writer.write_collection_of_primitive_values('nextExpectedRanges', self.next_expected_ranges)
        writer.write_additional_data(self.additional_data)

    def get_field_deserializers(self) -> Dict[str, any]:
        return {
            'uploadUrl':
            lambda parse_node: self.set_upload_url(parse_node.get_string_value()),
            'expirationDateTime':
            lambda parse_node: self.set_expiration_date_time(parse_node.get_date_time_value()),
            'isCancelled':
            lambda parse_node: self.set_is_cancelled(parse_node.get_boolean_value()),
            'nextExpectedRanges':
            lambda parse_node: self.
            set_next_expected_ranges(parse_node.get_collection_of_primitive_values('string'))
        }
