import pytest
from dotenv import load_dotenv
load_dotenv()

from src.ingestion.notifications import send_slack_alert
pytestmark = pytest.mark.unit


def test_send_slack_alert():
    send_slack_alert(
        operation_name="Test Slack Alert",
        exc=Exception("This is a test alert")
    )