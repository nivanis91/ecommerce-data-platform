from unittest.mock import Mock
import requests
import pytest
from src.ingestion.utils import retry_operation, should_retry_weather
pytestmark = pytest.mark.unit

def fake_operation_wrapper():
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

        return 'success'
    
    return fake_operation_func


def test_two_fails_then_success():
    mock_listener = Mock()

    def should_retry_weather_wrapper(exc):
        mock_listener(exc)
        return should_retry_weather(exc)

    result = retry_operation(
        fake_operation_wrapper(),
        should_retry_weather_wrapper
    )

    calls = mock_listener.call_args_list

    # make sure only two exception were thrown
    assert len(calls) == 2

    # check each exception
    assert str(calls[0].args[0]) == "429 Too Many Requests" and isinstance(calls[0].args[0], requests.exceptions.HTTPError)
    assert str(calls[1].args[0]) == "429 Too Many Requests" and isinstance(calls[1].args[0], requests.exceptions.HTTPError)

    # operation executed and returned a result
    assert result == 'success'

def test_retries_exhausted():
    mock_listener = Mock()

    def should_retry_weather_wrapper(exc):
        mock_listener(exc)
        return should_retry_weather(exc)

    def failing_operation():
        response = Mock(status_code=429)

        error = requests.exceptions.HTTPError(
            "429 Too Many Requests"
        )
        error.response = response

        raise error

    with pytest.raises(requests.exceptions.HTTPError):
        retry_operation(
            failing_operation,
            should_retry_weather_wrapper
        )

    calls = mock_listener.call_args_list

    # Make sure retry logic was triggered three times
    assert len(calls) == 3

    # Check each exception
    for call in calls:
        error = call.args[0]

        assert isinstance(error, requests.exceptions.HTTPError)
        assert error.response.status_code == 429
        assert str(error) == "429 Too Many Requests"