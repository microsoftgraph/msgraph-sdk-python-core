from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

from kiota_abstractions.serialization.additional_data_holder import AdditionalDataHolder
from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.serialization.parse_node import ParseNode
from kiota_abstractions.serialization.serialization_writer import SerializationWriter


class LargeFileUploadSession(Parsable, AdditionalDataHolder):

    def __init__(
        self,
        upload_url: Optional[str] = None,
        expiration_date_time: Optional[datetime] = None,
        additional_data: Optional[List[Dict[str, Any]]] = None,
        is_cancelled: Optional[bool] = False,
        next_expected_ranges: Optional[List[str]] = None
    ):
        self._upload_url = upload_url
        self._expiration_date_time = expiration_date_time
        self.additional_data = additional_data if additional_data is not None else []
        self.is_cancelled = is_cancelled
        self.next_expected_ranges = next_expected_ranges if next_expected_ranges is not None else []

    @property
    def upload_url(self):
        return self._upload_url

    @upload_url.setter
    def upload_url(self, value):
        self._upload_url = value

    @property
    def expiration_date_time(self):
        return self._expiration_date_time

    @expiration_date_time.setter
    def expiration_date_time(self, value):
        self._expiration_date_time = value

    @property
    def additional_data(self):
        return self._additional_data

    @additional_data.setter
    def additional_data(self, value):
        self._additional_data = value if value is not None else []

    @property
    def is_cancelled(self):
        return self._is_cancelled

    @is_cancelled.setter
    def is_cancelled(self, value):
        self._is_cancelled = value

    @property
    def next_expected_ranges(self):
        return self._next_expected_ranges

    @next_expected_ranges.setter
    def next_expected_ranges(self, value):
        self._next_expected_ranges = value if value is not None else []

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

    def get_field_deserializers(self) -> Dict[str, Any]:
        return {
            'upload_url':
            lambda parse_node: setattr(self, 'upload_url', parse_node.get_str_value()),
            'expiration_date_time':
            lambda parse_node:
            setattr(self, 'expiration_date_time', parse_node.get_datetime_value()),
            'is_cancelled':
            lambda parse_node: setattr(self, 'is_cancelled', parse_node.get_bool_value()),
            'next_expected_ranges':
            lambda parse_node: setattr(
                self, 'next_expected_ranges', parse_node.
                get_collection_of_primitive_values('string')
            )
        }
