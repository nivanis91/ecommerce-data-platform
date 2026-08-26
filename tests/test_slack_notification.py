import pytest

from src.ingestion.notifications import slack_alert_for
from src.ingestion.utils import retry_operation
from unittest.mock import Mock

pytestmark = pytest.mark.unit

def test_retry_operation_calls_slack_alert_on_exhaustion(monkeypatch):

    mock_send_slack_alert = Mock()
    error = Exception("Operation failed")

    def failing_operation():
            raise error

    monkeypatch.setattr(
        "src.ingestion.notifications.send_slack_alert",
        mock_send_slack_alert
    )

    with pytest.raises(Exception):
        retry_operation(
            operation=failing_operation,
            should_retry=lambda exc: True,
            max_attempts=3,
            on_exhausted=slack_alert_for("Test retry exhaustion")
        )

    mock_send_slack_alert.assert_called_once_with(
         "Test retry exhaustion",
         error
    )