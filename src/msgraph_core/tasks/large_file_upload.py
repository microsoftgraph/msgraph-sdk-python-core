import logging
import os
from asyncio import Future
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any, Optional, Tuple, TypeVar, Union

from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParsableFactory

from msgraph_core.models import LargeFileUploadSession, UploadResult  # check imports

T = TypeVar('T', bound=Parsable)


# pylint: disable=too-many-instance-attributes
class LargeFileUploadTask:

    def __init__(
        self,
        upload_session: Parsable,
        request_adapter: RequestAdapter,
        stream: BytesIO,
        parsable_factory: Optional[ParsableFactory] = None,
        max_chunk_size: int = 5 * 1024 * 1024
    ):
        self._upload_session = upload_session
        self._request_adapter = request_adapter
        self.stream = stream
        try:
            self.file_size = stream.getbuffer().nbytes
        except AttributeError:
            self.file_size = os.stat(stream.name).st_size
        self.max_chunk_size = max_chunk_size
        self.factory = parsable_factory
        cleaned_value = self.check_value_exists(
            upload_session, 'get_next_expected_range', ['next_expected_range', 'NextExpectedRange']
        )
        self.next_range = cleaned_value[1] if cleaned_value[0] else None
        self._chunks = int((self.file_size / max_chunk_size) + 0.5)
        self.on_chunk_upload_complete: Optional[Callable[[list[int]], None]] = None

    @property
    def upload_session(self):
        return self._upload_session

    @upload_session.setter
    def upload_session(self, value):
        self._upload_session = value

    @property
    def request_adapter(self):
        return self._request_adapter

    @property
    def chunks(self):
        return self._chunks

    @chunks.setter
    def chunks(self, value):
        self._chunks = value

    def upload_session_expired(self, upload_session: Optional[Parsable] = None) -> bool:
        now = datetime.now(timezone.utc)
        upload_session = upload_session or self.upload_session
        if not hasattr(upload_session, "expiration_date_time"):
            raise ValueError("Upload session does not have an expiration date time")
        expiry = getattr(upload_session, 'expiration_date_time')
        if expiry is None:
            raise ValueError("Expiry is None")
        if isinstance(expiry, str):
            then = datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%S")
        elif isinstance(expiry, datetime):
            then = expiry
        else:
            raise ValueError("Expiry is not a string or datetime")
        interval = now - then
        if not isinstance(interval, timedelta):
            raise ValueError("Interval is not a timedelta")
        if interval.total_seconds() >= 0:
            return True
        return False

    async def upload(self, after_chunk_upload: Optional[Callable] = None):
        # Rewind at this point to take care of failures.
        self.stream.seek(0)
        if self.upload_session_expired(self.upload_session):
            raise RuntimeError('The upload session is expired.')

        self.on_chunk_upload_complete = after_chunk_upload or self.on_chunk_upload_complete
        session: LargeFileUploadSession = await self.next_chunk(
            self.stream, 0, max(0, min(self.max_chunk_size - 1, self.file_size - 1))
        )
        process_next = session
        # determine the range  to be uploaded
        # even when resuming existing upload sessions.
        range_parts = self.next_range[0].split("-") if self.next_range else ['0', '0']
        end = min(int(range_parts[0]) + self.max_chunk_size - 1, self.file_size)
        uploaded_range = [range_parts[0], end]
        response = None

        while self.chunks >= 0:
            session = process_next
            if self.chunks == 0:
                # last chunk
                response = await self.last_chunk(self.stream)

            try:
                lfu_session = session
                if lfu_session is None:
                    continue
                next_range = None
                if hasattr(lfu_session, 'next_expected_ranges'):
                    next_range = lfu_session.next_expected_ranges
                old_url = self.get_validated_upload_url(self.upload_session)
                if hasattr(lfu_session, 'upload_url'):
                    lfu_session.upload_url = old_url
                if self.on_chunk_upload_complete is not None:
                    self.on_chunk_upload_complete(uploaded_range)
                if not next_range:
                    continue
                range_parts = str(next_range[0]).split("-")
                end = min(int(range_parts[0]) + self.max_chunk_size, self.file_size)
                uploaded_range = [range_parts[0], end]
                self.next_range = next_range[0] + "-"
                process_next = await self.next_chunk(self.stream)

            except Exception as error:  #pylint: disable=broad-except
                logging.error("Error uploading chunk  %s", error)
            finally:
                self.chunks -= 1
        upload_result: UploadResult[Any] = UploadResult()
        upload_result.item_response = response
        if hasattr(self.upload_session, 'upload_url'):
            upload_result.location = self.upload_session.upload_url
        return upload_result

    @property
    def next_range(self):
        return self._next_range

    @next_range.setter
    def next_range(self, value: Optional[str]) -> None:
        self._next_range = value

    async def next_chunk(
        self, file: BytesIO, range_start: int = 0, range_end: int = 0
    ) -> LargeFileUploadSession:
        upload_url = self.get_validated_upload_url(self.upload_session)
        if not upload_url:
            raise ValueError('The upload session URL must not be empty.')
        info = RequestInformation()
        info.url = upload_url
        info.http_method = Method.PUT
        if not self.next_range:
            self.next_range = f'{range_start}-{range_end}'
        range_parts = self.next_range.split('-') if self.next_range else ['-']
        start = int(range_parts[0])
        end = int(range_parts[1]) if len(range_parts) > 1 else 0
        if start == 0 and end == 0:
            chunk_data = file.read(self.max_chunk_size)
            end = min(self.max_chunk_size - 1, self.file_size - 1)
        elif start == 0:
            chunk_data = file.read(end + 1)
        elif end == 0:
            file.seek(start)
            chunk_data = file.read(self.max_chunk_size)
            end = start + len(chunk_data) - 1
        else:
            file.seek(start)
            end = min(end, self.max_chunk_size + start)
            chunk_data = file.read(end - start + 1)
        info.headers = HeadersCollection()

        info.headers.try_add('Content-Range', f'bytes {start}-{end}/{self.file_size}')
        info.headers.try_add('Content-Length', str(len(chunk_data)))
        info.headers.try_add("Content-Type", "application/octet-stream")
        info.set_stream_content(bytes(chunk_data))
        error_map: dict[str, int] = {}
        return await self.request_adapter.send_async(info, LargeFileUploadSession, error_map)

    async def last_chunk(
        self,
        file: BytesIO,
        range_start: int = 0,
        range_end: int = 0,
        parsable_factory: Optional[ParsableFactory] = None
    ) -> Optional[Union[T, bytes]]:
        upload_url = self.get_validated_upload_url(self.upload_session)
        if not upload_url:
            raise ValueError('The upload session URL must not be empty.')
        info = RequestInformation()
        info.url = upload_url
        info.http_method = Method.PUT
        if not self.next_range:
            self.next_range = f'{range_start}-{range_end}'
        range_parts = self.next_range.split('-') if self.next_range else ['-']
        start = int(range_parts[0])
        end = int(range_parts[1]) if len(range_parts) > 1 else 0
        if start == 0 and end == 0:
            chunk_data = file.read(self.max_chunk_size)
            end = min(self.max_chunk_size - 1, self.file_size - 1)
        elif start == 0:
            chunk_data = file.read(end + 1)
        elif end == 0:
            file.seek(start)
            chunk_data = file.read(self.max_chunk_size)
            end = start + len(chunk_data) - 1
        else:
            file.seek(start)
            end = min(end, self.max_chunk_size + start)
            chunk_data = file.read(end - start + 1)
        info.headers = HeadersCollection()

        info.headers.try_add('Content-Range', f'bytes {start}-{end}/{self.file_size}')
        info.headers.try_add('Content-Length', str(len(chunk_data)))
        info.headers.try_add("Content-Type", "application/octet-stream")
        info.set_stream_content(bytes(chunk_data))
        error_map: dict[str, int] = {}
        factory = self.factory or parsable_factory
        if factory:
            return await self.request_adapter.send_async(info, factory, error_map)
        return await self.request_adapter.send_primitive_async(info, "bytes", error_map)

    def get_file(self) -> BytesIO:
        return self.stream

    async def cancel(self) -> Parsable:
        upload_url = self.get_validated_upload_url(self.upload_session)
        request_information = RequestInformation(method=Method.DELETE, url_template=upload_url)

        await self.request_adapter.send_no_response_content_async(request_information)

        if hasattr(self.upload_session, 'is_cancelled'):
            self.upload_session.is_cancelled = True
        elif hasattr(self.upload_session,
                     'additional_data') and hasattr(self.upload_session, 'additional_data'):
            current = self.upload_session.additional_data
            new = {**current, 'is_cancelled': True}
            self.upload_session.additional_data = new

        return self.upload_session

    def additional_data_contains(self, parsable: Parsable,
                                 property_candidates: list[str]) -> Tuple[bool, Any]:
        if not issubclass(type(parsable), AdditionalDataHolder):
            raise ValueError(
                'The object passed does not contain property/properties '
                f'{",".join(property_candidates)} and does not implement '
                'AdditionalDataHolder'
            )
        if not hasattr(parsable, 'additional_data'):
            raise ValueError('The object passed does not contain an additional_data property')
        additional_data = parsable.additional_data
        for property_candidate in property_candidates:
            if property_candidate in additional_data:
                return True, additional_data[property_candidate]
        return False, None

    def check_value_exists(
        self, parsable: Parsable, attribute_name: str, property_names_in_additional_data: list[str]
    ) -> Tuple[bool, Any]:
        checked_additional_data = self.additional_data_contains(
            parsable, property_names_in_additional_data
        )
        if issubclass(type(parsable), AdditionalDataHolder) and checked_additional_data[0]:
            return True, checked_additional_data[1]

        if hasattr(parsable, attribute_name):
            return True, getattr(parsable, attribute_name)

        return False, None

    async def resume(self) -> Future:
        if self.upload_session_expired(self.upload_session):
            raise RuntimeError('The upload session is expired.')

        validated_value = self.check_value_exists(
            self.upload_session, 'next_expected_ranges',
            ['NextExpectedRanges', 'nextExpectedRanges']
        )
        if not validated_value[0]:
            raise RuntimeError(
                'The object passed does not contain a valid "nextExpectedRanges" property.'
            )

        next_ranges: list[str] = validated_value[1]
        if len(next_ranges) == 0:
            raise RuntimeError('No more bytes expected.')

        next_range = next_ranges[0]
        self.next_range = next_range
        return await self.upload()

    def get_validated_upload_url(self, upload_session: Parsable) -> str:
        if not hasattr(upload_session, 'upload_url'):
            raise RuntimeError('The upload session does not contain a valid upload url')
        result = upload_session.upload_url

        if result is None or result.strip() == '':
            raise RuntimeError('The upload URL cannot be empty.')
        return result

    def get_next_range(self) -> Optional[str]:
        return self.next_range

    def get_file_size(self) -> int:
        return self.file_size
