from typing import Callable, Optional, List, Tuple, Any
from io import BytesIO
from datetime import datetime
from asyncio import Future

from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization.additional_data_holder import AdditionalDataHolder

from msgraph_core.models import LargeFileUploadCreateSession, LargeFileUploadSession  # check imports


class LargeFileUploadTask:

    def __init__(
        self,
        upload_session: Parsable,
        request_adapter: RequestAdapter,
        stream: BytesIO,  # counter check this
        max_chunk_size: int = 4 * 1024 * 1024
    ):
        self.upload_session = upload_session
        self.request_adapter = request_adapter
        self.stream = stream
        self.file_size = stream.getbuffer().nbytes
        self.max_chunk_size = max_chunk_size
        cleaned_value = self.check_value_exists(
            upload_session, 'get_next_expected_range', ['next_expected_range', 'NextExpectedRange']
        )
        self.next_range = cleaned_value[0]
        self.chunks = int((self.file_size / max_chunk_size) + 0.5)
        self.on_chunk_upload_complete: Optional[Callable[[int, int], None]] = None

    def get_upload_session(self) -> Parsable:
        return self.upload_session

    def create_upload_session(
        self,
        request_body: LargeFileUploadSession,
        model: LargeFileUploadCreateSession,
    ) -> Future:
        request_info = RequestInformation()
        request_info.url = request_info.url  # check the URL
        request_info.http_method = Method.POST
        request_info.set_content_from_parsable(
            self.request_adapter, 'application/json', request_body
        )
        request_info.set_stream_content(model)

        return self.request_adapter.send_async(request_info, LargeFileUploadSession, {})

    def get_adapter(self) -> RequestAdapter:
        return self.request_adapter

    def get_chunks(self) -> int:
        return self.chunks

    def upload_session_expired(self, upload_session: Optional[Parsable] = None) -> bool:
        now = datetime.now()

        validated_value = self.check_value_exists(
            upload_session or self.upload_session, 'get_expiration_date_time',
            ['ExpirationDateTime', 'expirationDateTime']
        )
        if not validated_value[0]:
            raise Exception('The upload session does not contain an expiry datetime.')

        expiry = validated_value[1]

        if expiry is None:
            raise ValueError('The upload session does not contain a valid expiry date.')

        then = datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%S")
        interval = (now - then).total_seconds()

        if interval < 0:
            return True
        return False

    async def upload(self, after_chunk_upload: Optional[Callable] = None) -> Future:
        # Rewind to take care of failures.
        self.stream.seek(0)
        if self.upload_session_expired(self.upload_session):
            raise RuntimeError('The upload session is expired.')

        self.on_chunk_upload_complete = after_chunk_upload if after_chunk_upload is not None else self.on_chunk_upload_complete
        session = self.next_chunk(
            self.stream, 0, max(0, min(self.max_chunk_size - 1, self.file_size - 1))
        )
        process_next = session
        # includes when resuming existing upload sessions.
        range_parts = self.next_range[0].split("-") if self.next_range else ['0', '0']
        end = min(int(range_parts[0]) + self.max_chunk_size - 1, self.file_size)
        uploaded_range = [range_parts[0], end]
        while self.chunks > 0:
            session = process_next
            process_next = session.then(
                lambda upload_session: self.process_chunk(upload_session, uploaded_range),
                lambda error: self.handle_error(error)
            )
            if process_next is not None:
                await process_next
            self.chunks -= 1
        return session

    def process_chunk(self, upload_session, uploaded_range):
        if upload_session is None:
            return None

        next_range = upload_session.get_next_expected_ranges()
        if not next_range:
            return upload_session

        old_url = self.get_validated_upload_url(self.upload_session)
        upload_session.set_upload_url(old_url)

        if self.on_chunk_upload_complete is not None:
            self.on_chunk_upload_complete(uploaded_range)

        range_parts = next_range[0].split("-")
        end = min(int(range_parts[0]) + self.max_chunk_size, self.file_size)
        self.set_next_range(f"{range_parts[0]}-{end}")

        self.next_chunk(self.stream)

        return upload_session

    def handle_error(self, error):
        raise error

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

        info.headers = {
            **info.request_headers(), 'Content-Range': f'bytes {start}-{end}/{self.file_size}'
        }

        info.headers = {**info.request_headers(), 'Content-Length': str(len(chunk_data))}

        info.set_stream_content(BytesIO(chunk_data))
        return await self.request_adapter.send_async(
            info, LargeFileUploadSession.create_from_discriminator_value
        )

    def get_file(self) -> BytesIO:
        return self.stream

    async def cancel(self) -> Optional[Future]:
        upload_url = self.get_validated_upload_url(self.upload_session)
        request_information = RequestInformation(http_method=Method.DELETE, url=upload_url)

        await self.request_adapter.send_no_response_content_async(request_information)

        if hasattr(self.upload_session, 'set_is_cancelled'):
            self.upload_session.set_is_cancelled(True)
        elif hasattr(self.upload_session, 'set_additional_data'
                     ) and hasattr(self.upload_session, 'get_additional_data'):
            current = self.upload_session.get_additional_data()
            new = {**current, 'is_cancelled': True}
            self.upload_session.set_additional_data(new)

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
        self, parsable: Parsable, getter_name: str, property_names_in_additional_data: List[str]
    ) -> Tuple[bool, Any]:
        checked_additional_data = self.additional_data_contains(
            parsable, property_names_in_additional_data
        )
        if issubclass(type(parsable), AdditionalDataHolder) and checked_additional_data[0]:
            return True, checked_additional_data[1]

        if hasattr(parsable, getter_name):
            return True, getattr(parsable, getter_name)()

        return False, None

    async def resume(self) -> Future:
        if self.upload_session_expired(self.upload_session):
            raise RuntimeError('The upload session is expired.')

        validated_value = self.check_value_exists(
            self.upload_session, 'get_next_expected_ranges',
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
        if not hasattr(upload_session, 'get_upload_url'):
            raise RuntimeError('The upload session does not contain a valid upload url')
        result = upload_session.get_upload_url()

        if result is None or result.strip() == '':
            raise RuntimeError('The upload URL cannot be empty.')
        return result

    def get_next_range(self) -> Optional[str]:
        return self.next_range

    def get_file_size(self) -> int:
        return self.file_size
