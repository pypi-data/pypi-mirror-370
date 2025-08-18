import json
import traceback

from cc_py_commons.config.env import app_config
from cc_py_commons.sqs.sqs_service import SqsService
from cc_py_commons.utils.logger_v2 import logger

class BookingAssistantQuoteCancelNotification:

	def send(self, load_id):
		'''
		Sends and event to the Booking Assistant Flow SQS queue specified in the config.
		Returns the messageId of the enqueued message for later retrieval.
		'''
		event = {
			'loadId': str(load_id),
			'subject': app_config.BOOKING_ASSISTANT_QUOTE_CANCEL_SUBJECT,
			'className': app_config.BOOKING_ASSISTANT_QUOTE_CANCEL_CLASS_NAME
		}
		logger.debug(f"sending event {event} to {app_config.BOOKING_ASSISTANT_FLOW_QUEUE}")

		try:
			sqs_service = SqsService()
			return sqs_service.send(app_config.BOOKING_ASSISTANT_FLOW_QUEUE, json.dumps(event), app_config.BOOKING_ASSISTANT_DELAY_SECONDS)
		except Exception as e:
			logger.error(json.dumps({
				'message': 'Failed to send class BookingAssistantQuoteCancelNotification',
				'error': str(e),
				'sta_cktrace': traceback.format_exc(),
				'event': event
			}))
