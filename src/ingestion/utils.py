import time
import requests

RETRYABLE_HTTP_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}

RETRYABLE_WEATHER_STATUS_CODES = RETRYABLE_HTTP_STATUS_CODES

def retry_operation(
        operation, 
        should_retry, 
        max_attempts=3
    ):

    for current_attempt in range(max_attempts):
        try:
            return operation()
        except should_retry:
            if current_attempt == max_attempts - 1:
                raise

            # Double the wait time, afer each failed attempt
            wait_time = 2 ** current_attempt
            print(
                f"BigQuery operation failed. "
                f"Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)


# Retry transient HTTP errors (429/5xx), timeouts, and connection failures.
def should_retry_weather(exc):
    if isinstance(exc, requests.HTTPError):
        return exc.response.status_code in RETRYABLE_WEATHER_STATUS_CODES

    return isinstance(
        exc,
        (
            requests.Timeout,
            requests.ConnectionError,
        )
    )