import json
import traceback

from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils import json_logger


def execute(email_message_id, event_type, topic_arn):
	event_type_email_status_map = {
		'open': 'OPENED',
		'click': 'CLICKED',
		'delivered': 'DELIVERED',
		'replied': 'REPLIED'
	}
	if event_type not in event_type_email_status_map:
		json_logger.warning(None, 'Unsupported email event type', email_message_id = email_message_id,
			event_type = event_type, topic_arn = topic_arn)
		return False
	try:
		subject = "handle-procured-carrier-email-event"
		message = {
			"subject": subject,
			"className": "com.cargochief.sdk.carrierhub.notifications.ProcuredCarrierEmailEventNotification",
			"emailStatus": event_type_email_status_map[event_type],
			"emailMessageId": email_message_id
		}
		sns_service = SnsService()
		sns_service.send(topic_arn, message.get('subject'), json.dumps(message))
		return True
	except Exception as e:
		json_logger.error(None, 'Failed to send procured carrier email event',
						  email_message_id=email_message_id, event_type=event_type, topic_arn=topic_arn,
						  error=str(e), stacktrace=traceback.format_exc())
		return False
