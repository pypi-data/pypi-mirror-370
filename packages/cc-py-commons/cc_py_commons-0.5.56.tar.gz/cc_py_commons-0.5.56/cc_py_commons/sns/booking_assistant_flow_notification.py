import json
import traceback

from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils import json_logger


class BookingAssistantFlowNotification:

	def __init__(self, app_config):
		self._app_config = app_config

	def send(self, user_id, load, params, capacity_search_equipments, request_id, auto_invite_details=None):
		'''
	  Sends and event to the Booking Assistant Flow SQS queue specified in the config.
	  Returns the messageId of the enqueued message for later retrieval.
	  '''
		c4_account_id = load.get('accountId')
		subject = self._app_config.BOOKING_ASSISTANT_SNS_SUBJECT
		event = {
			'userId': user_id,
			'loadDTO': load,
			'payload': params,
			'capacitySearchEquipments': capacity_search_equipments,
			'requestId': request_id,
			'subject': f'{subject}',
			'className': f'{self._app_config.BOOKING_ASSISTANT_SNS_CLASS_NAME}',
			'autoInviteDetails': auto_invite_details
		}
		json_logger.debug(c4_account_id, 'Sending booking assistant flow SNS notification',
						  topic=self._app_config.BOOKING_ASSISTANT_SNS_TOPIC_ARN, event=event)
		try:
			sns_service = SnsService()
			return sns_service.send(self._app_config.BOOKING_ASSISTANT_SNS_TOPIC_ARN, subject, json.dumps(event))
		except Exception as e:
			json_logger.warning(c4_account_id, 'Failed to send BookingAssistantFlowNotification',
								error=str(e), stacktrace=traceback.format_exc())
