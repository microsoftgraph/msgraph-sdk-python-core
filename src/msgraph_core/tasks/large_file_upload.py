from typing import Callable, Optional, List, Tuple, Any, Dict
from io import BytesIO
from asyncio import Future
from datetime import datetime, timedelta

from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.method import Method
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_http.httpx_request_adapter import HttpxRequestAdapter as RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization.additional_data_holder import AdditionalDataHolder

from msgraph_core.models import LargeFileUploadCreateSessionBody, LargeFileUploadSession  # check imports


class LargeFileUploadTask:

    def __init__(
        self,
        upload_session: LargeFileUploadSession,
        request_adapter: RequestAdapter,
        stream: BytesIO,  # counter check this
        max_chunk_size: int = 1024  # 4 * 1024 * 1024 - use smaller chnuks for testing
    ):
        self._upload_session = upload_session
        self._request_adapter = request_adapter
        self.stream = stream
        self.file_size = stream.getbuffer().nbytes
        self.max_chunk_size = max_chunk_size
        cleaned_value = self.check_value_exists(
            upload_session, 'get_next_expected_range', ['next_expected_range', 'NextExpectedRange']
        )
        self.next_range = cleaned_value[0]
        self._chunks = int((self.file_size / max_chunk_size) + 0.5)
        self.on_chunk_upload_complete: Optional[Callable[[int, int], None]] = None

    @property
    def upload_session(self) -> Parsable:
        return self._upload_session

    @staticmethod
    async def create_upload_session(request_adapter: RequestAdapter, request_body, url: str):
        request_information = RequestInformation()
        base_url = request_adapter.base_url.rstrip('/')
        path = url.lstrip('/')
        new_url = f"{base_url}/{path}"
        print(f"New url {new_url}")
        request_information.url = new_url
        request_information.http_method = Method.POST
        request_information.set_content_from_parsable(
            request_adapter, 'application/json', request_body
        )
        error_map: Dict[str, int] = {}

        return await request_adapter.send_async(
            request_information, LargeFileUploadSession.create_from_discriminator_value, error_map
        )

    @property
    def request_adapter(self) -> RequestAdapter:
        return self._request_adapter

    @property
    def chunks(self) -> int:
        return self._chunks

    def upload_session_expired(self, upload_session: LargeFileUploadSession = None) -> bool:
        now = datetime.now()
        upload_session = upload_session or self._upload_session
        if not hasattr(upload_session, "expiration_date_time"):
            raise ValueError("Upload session does not have an expiration date time")
        expiry = upload_session.expiration_date_time
        print(expiry)
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
        if interval.total_seconds() <= 0:
            return True
        return False

    async def upload(self, after_chunk_upload=None):
        # Rewind at this point to take care of failures.
        self.stream.seek(0)
        if self.upload_session_expired(self.upload_session):
            raise RuntimeError('The upload session is expired.')

        self.on_chunk_upload_complete = after_chunk_upload if self.on_chunk_upload_complete is None else self.on_chunk_upload_complete
        session = await self.next_chunk(
            self.stream, 0, max(0, min(self.max_chunk_size - 1, self.file_size - 1))
        )
        process_next = session
        # determine the range  to be uploaded
        # even when resuming existing upload sessions.
        range_parts = self.next_range[0].split("-") if self.next_range else ['0', '0']
        end = min(int(range_parts[0]) + self.max_chunk_size - 1, self.file_size)
        uploaded_range = [range_parts[0], end]
        print(f"File size {self.file_size}")
        while self.chunks > 0:
            session = process_next
            future = Future()

            def success_callback(large_file_uploasd_session):
                nonlocal process_next, uploaded_range

                if large_file_uploasd_session is None:
                    return large_file_uploasd_session

                next_range = large_file_uploasd_session.next_expected_ranges
                old_url = self.get_validated_upload_url(self.upload_session)
                large_file_uploasd_session.upload_url = old_url

                if self.on_chunk_upload_complete is not None:
                    self.on_chunk_upload_complete(uploaded_range)

                if not next_range:
                    return large_file_uploasd_session

                range_parts = next_range[0].split("-")
                end = min(int(range_parts[0]) + self.max_chunk_size, self.file_size)
                uploaded_range = [range_parts[0], end]
                self.set_next_range(next_range[0] + "-")
                process_next = self.next_chunk(self.stream)

                return large_file_uploasd_session

        def failure_callback(error):
            raise error

        future.add_done_callback(success_callback)
        future.set_exception_callback(failure_callback)

        if future is not None:
            future.result()  # This will block until the future is resolved

        self.chunks -= 1

        return session

    def set_next_range(self, next_range: Optional[str]) -> None:
        self.next_range = next_range

    async def next_chunk(self, file: BytesIO, range_start: int = 0, range_end: int = 0) -> Future:
        upload_url = self.get_validated_upload_url(self.upload_session)

        if not upload_url:
            raise ValueError('The upload session URL must not be empty.')
        info = RequestInformation()
        info.url = upload_url
        info.http_method = Method.PUT
        if not self.next_range:
            self.set_next_range(f'{range_start}-{range_end}')
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
        print(f"Chunk data {chunk_data}")
        info.headers = HeadersCollection()

        info.headers.try_add('Content-Range', f'bytes {start}-{end}/{self.file_size}')
        # info.headers.try_add(**info.request_headers) what do we do if headers need to be passed
        info.headers.try_add('Content-Length', str(len(chunk_data)))
        info.set_stream_content(BytesIO(chunk_data))
        error_map: Dict[str, int] = {}

        parsable_factory: LargeFileUploadSession[Any] = self.upload_session

        print(f"Body {LargeFileUploadSession.create_from_discriminator_value}")
        print(f"Upload session url {self.upload_session.upload_url}")
        print(f"Expiraton date {self.upload_session.expiration_date_time}")
        print(f"Additional data {self.upload_session.additional_data}")
        print(f"Session is canceled {self.upload_session.is_cancelled}")
        print(f"Next expected ranges {self.upload_session.next_expected_ranges}")
        return await self.request_adapter.send_async(info, parsable_factory, error_map)

    def get_file(self) -> BytesIO:
        return self.stream

    async def cancel(self) -> Optional[Future]:
        upload_url = self.get_validated_upload_url(self.upload_session)
        request_information = RequestInformation(http_method=Method.DELETE, url=upload_url)

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
                                 property_candidates: List[str]) -> Tuple[bool, Any]:
        if not issubclass(type(parsable), AdditionalDataHolder):
            raise ValueError(
                f'The object passed does not contain property/properties {",".join(property_candidates)} and does not implement AdditionalDataHolder'
            )
        additional_data = parsable.additional_data
        for property_candidate in property_candidates:
            if property_candidate in additional_data:
                return True, additional_data[property_candidate]
        return False, None

    def check_value_exists(
        self, parsable: Parsable, attribute_name: str, property_names_in_additional_data: List[str]
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

        next_ranges: List[str] = validated_value[1]
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
