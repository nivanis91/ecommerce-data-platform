import os
import requests
import logging
logger = logging.getLogger(__name__)

def slack_alert_for(operation_name):
    def alert(exception):
        send_slack_alert(
            operation_name,
            exception
        )

    return alert

def send_slack_alert(operation_name, exc):
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]

    message = (
        "🚨 Data pipeline alert\n\n"
        f"Retry attempts exhausted.\n"
        f"Error: {exc}"
    )

    try:
        requests.post(
            webhook_url,
            json={"text": message},
            timeout=10
        )
    except Exception:
        logger.exception("Failed to send Slack alert")