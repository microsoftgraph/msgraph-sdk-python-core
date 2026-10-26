from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import Mock

import pytest

from msgraph_core.models import LargeFileUploadSession
from msgraph_core.tasks.large_file_upload import LargeFileUploadTask


def create_upload_task(expiration_date_time):
    upload_session = LargeFileUploadSession(
        expiration_date_time=expiration_date_time,
        next_expected_ranges=['0-'],
        upload_url='https://example.org/upload',
    )
    return LargeFileUploadTask(upload_session, Mock(), BytesIO(b'test payload'))


def test_upload_session_expired_with_naive_datetime():
    expiration_date_time = (datetime.now(timezone.utc) - timedelta(minutes=5)).replace(tzinfo=None)
    task = create_upload_task(expiration_date_time)

    assert task.upload_session_expired() is True


def test_upload_session_not_expired_with_naive_datetime():
    expiration_date_time = (datetime.now(timezone.utc) + timedelta(minutes=5)).replace(tzinfo=None)
    task = create_upload_task(expiration_date_time)

    assert task.upload_session_expired() is False


def test_upload_session_expired_with_offset_aware_datetime():
    expiration_date_time = datetime.now(
        timezone(timedelta(hours=-5))
    ) - timedelta(minutes=5)
    task = create_upload_task(expiration_date_time)

    assert task.upload_session_expired() is True


def test_upload_session_not_expired_with_offset_aware_datetime():
    expiration_date_time = datetime.now(
        timezone(timedelta(hours=-5))
    ) + timedelta(minutes=5)
    task = create_upload_task(expiration_date_time)

    assert task.upload_session_expired() is False


@pytest.mark.parametrize(
    ('expiration_date_time', 'expected'),
    [
        ((datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace('+00:00', 'Z'), True),
        ((datetime.now(timezone.utc) + timedelta(minutes=5)).astimezone(
            timezone(timedelta(hours=2))
        ).isoformat(), False),
    ],
)
def test_upload_session_expired_with_iso8601_string(expiration_date_time, expected):
    task = create_upload_task(expiration_date_time)

    assert task.upload_session_expired() is expected
