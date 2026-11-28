import re
from datetime import datetime, timedelta, timezone
from io import BytesIO

import pytest

from msgraph_core.models import LargeFileUploadSession  # pylint: disable=no-name-in-module, import-error
from msgraph_core.tasks.large_file_upload import LargeFileUploadTask  # pylint: disable=no-name-in-module, import-error

CHUNK_SIZE = 320


class FakeUploadService:
    """Accepts byte ranges like a Graph upload session and records each PUT.

    open_ended=True answers nextExpectedRanges as "N-" (OneDrive),
    open_ended=False as "N" (Outlook attachments).
    """

    def __init__(self, size, open_ended, received=b""):
        self.size = size
        self.open_ended = open_ended
        self.data = bytearray(received)
        self.puts = []

    def _put(self, info):
        if len(self.data) == self.size:
            raise RuntimeError("upload session already completed")
        content_range = info.headers.get('Content-Range')
        content_range = next(iter(content_range))
        start, end, total = map(int, re.match(r'bytes (\d+)-(\d+)/(\d+)', content_range).groups())
        body = info.content
        self.puts.append((start, end))
        assert total == self.size
        assert start == len(self.data), f"expected range to start at {len(self.data)}"
        assert end - start + 1 == len(body)
        self.data += body
        if len(self.data) == self.size:
            return None
        return [f"{len(self.data)}-" if self.open_ended else str(len(self.data))]

    async def send_async(self, info, factory, error_map):
        next_ranges = self._put(info)
        if next_ranges is None and factory is not LargeFileUploadSession:
            return {"id": "uploaded-item"}
        return LargeFileUploadSession(next_expected_ranges=next_ranges)


def upload_session(next_expected_ranges=None):
    return LargeFileUploadSession(
        upload_url="https://example.com/upload",
        expiration_date_time=datetime.now(timezone.utc) + timedelta(days=1),
        next_expected_ranges=next_expected_ranges,
    )


def payload(size):
    return bytes(i % 251 for i in range(size))


@pytest.mark.asyncio
@pytest.mark.parametrize("open_ended", [True, False])
@pytest.mark.parametrize("size", [1, 100, CHUNK_SIZE, CHUNK_SIZE + 1, 1000, 3 * CHUNK_SIZE])
async def test_upload_sends_each_byte_once(size, open_ended):
    data = payload(size)
    service = FakeUploadService(size, open_ended)
    uploaded_ranges = []
    task = LargeFileUploadTask(
        upload_session(), service, BytesIO(data), lambda n: None, max_chunk_size=CHUNK_SIZE
    )

    result = await task.upload(uploaded_ranges.append)

    assert bytes(service.data) == data
    expected = [(s, min(s + CHUNK_SIZE, size) - 1) for s in range(0, size, CHUNK_SIZE)]
    assert service.puts == expected
    assert uploaded_ranges == [list(r) for r in expected]
    assert result.item_response == {"id": "uploaded-item"}
    assert result.location == "https://example.com/upload"


@pytest.mark.asyncio
@pytest.mark.parametrize("next_range", ["640-", "640"])
async def test_resume_continues_from_next_expected_range(next_range):
    data = payload(1000)
    service = FakeUploadService(1000, open_ended=True, received=data[:640])
    task = LargeFileUploadTask(
        upload_session([next_range]), service, BytesIO(data), max_chunk_size=CHUNK_SIZE
    )
    task.factory = lambda n: None

    result = await task.resume()

    assert bytes(service.data) == data
    assert service.puts == [(640, 959), (960, 999)]
    assert result.item_response == {"id": "uploaded-item"}


@pytest.mark.parametrize(
    "value,expected", [
        ("0-319", (0, 319)), ("535313-", (535313, 0)), ("535313", (535313, 0)),
        (["320-639", "700-"], (320, 639))
    ]
)
def test_parse_range(value, expected):
    assert LargeFileUploadTask._parse_range(value) == expected  # pylint: disable=protected-access
