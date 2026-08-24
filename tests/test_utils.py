from unittest.mock import Mock
import requests
import pytest
from src.ingestion.utils import retry_operation, should_retry_weather
pytestmark = pytest.mark.unit

def fake_operation_wrapper(mockFunc):
    attempt = 0

    def fake_operation_func():
        nonlocal attempt
        attempt += 1

        if attempt < 3:
            mock_response = Mock()
            mock_response.status_code = 429

            error = requests.exceptions.HTTPError("429 Too Many Requests")
            error.response = mock_response

            raise error

        mockFunc()

    return fake_operation_func


def test_two_fails_then_success(
):
    mock_operation = Mock()

    retry_operation(
        fake_operation_wrapper(mock_operation),
        should_retry_weather
    )

    mock_operation.assert_called_once()