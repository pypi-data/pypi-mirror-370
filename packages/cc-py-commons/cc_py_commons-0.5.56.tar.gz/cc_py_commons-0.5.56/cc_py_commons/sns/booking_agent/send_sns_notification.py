import json

from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils.logger_v2 import logger
from .constants import BOOKING_AGENT_TOPIC_ARN


def send_sns_notification(message):
    if message:
        logger.debug(f"booking_agent.send_sns_notification: Sending message {message} to {BOOKING_AGENT_TOPIC_ARN}")
        try:
            sns_service = SnsService()
            sns_service.send(BOOKING_AGENT_TOPIC_ARN, message.get('subject'), json.dumps(message))
        except Exception as e:
            logger.error(f"booking_agent.send_sns_notification: Failed to send notification message: {e}")
    else:
        logger.info("booking_agent.send_sns_notification: Notification not sent because message is empty or null")
