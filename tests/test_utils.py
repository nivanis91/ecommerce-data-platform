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
    mock_listener = Mock()

    def should_retry_weather_wrapper(exc):
        mock_listener(exc)
        return should_retry_weather(exc)

    retry_operation(
        fake_operation_wrapper(mock_operation),
        should_retry_weather_wrapper
    )

    calls = mock_listener.call_args_list

    # make sure only two exception werethrown
    assert len(calls) == 2

    # check each exception
    assert str(calls[0].args[0]) == "429 Too Many Requests" and isinstance(calls[0].args[0], requests.exceptions.HTTPError)
    assert str(calls[1].args[0]) == "429 Too Many Requests" and isinstance(calls[1].args[0], requests.exceptions.HTTPError)

    # success operation has been executed
    mock_operation.assert_called_once()