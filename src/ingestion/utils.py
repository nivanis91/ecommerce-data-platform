import time
import requests
import psycopg2
from google.api_core import exceptions
import logging
logger = logging.getLogger(__name__)
import botocore


RETRYABLE_HTTP_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}

RETRYABLE_WEATHER_STATUS_CODES = RETRYABLE_HTTP_STATUS_CODES

RETRYABLE_POSTGRES_ERRORS = (
    psycopg2.OperationalError,
)

RETRYABLE_BIGQUERY_ERRORS = (
    exceptions.TooManyRequests,       # 429
    exceptions.InternalServerError,   # 500
    exceptions.BadGateway,            # 502
    exceptions.ServiceUnavailable,    # 503
    exceptions.DeadlineExceeded,      # timeout
)

def retry_operation(
        operation, 
        should_retry, 
        max_attempts=3,
        on_exhausted=None
    ):

    for current_attempt in range(max_attempts):
        try:
            return operation()
        except Exception as exc:
            logger.warning("Operation failed: %s", exc)
            
            if not should_retry(exc):
                raise
            if current_attempt == max_attempts - 1:
                if on_exhausted:
                    on_exhausted(exc)
                    
                raise

            # Double the wait time, afer each failed attempt
            wait_time = 2 ** current_attempt
            logger.warning(
                "Retrying in %s seconds",
                wait_time
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

should_retry_postgres = lambda exc: isinstance(
            exc,
            RETRYABLE_POSTGRES_ERRORS
        )

should_retry_bigquery = lambda exc: isinstance(
            exc,
            RETRYABLE_BIGQUERY_ERRORS
        )

def should_retry_s3(exc):
    if not isinstance(exc, botocore.exceptions.ClientError):
        return False

    error_code = exc.response.get("Error", {}).get("Code")

    return error_code in {
        "RequestTimeout",
        "RequestTimeTooSkewed",
        "SlowDown",
        "InternalError",
        "ServiceUnavailable",
    }