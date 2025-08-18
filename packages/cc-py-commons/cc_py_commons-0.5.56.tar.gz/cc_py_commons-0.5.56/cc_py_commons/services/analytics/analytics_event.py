import json

from cc_py_commons.config.env import app_config
from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils import json_logger


def send(c4_user_id, c4_account_id, event_type, payload):
	user_data = {'id': c4_user_id, 'accountId': c4_account_id}
	analytics_payload = {**payload, **user_data, 'eventType': event_type}
	json_logger.debug(c4_account_id, 'Sending analytics SNS notification',
					  topic=app_config.ANALYTICS_SNS_ARN, event_type=event_type, payload=analytics_payload)
	sns_service = SnsService()
	sns_service.send(app_config.ANALYTICS_SNS_ARN, analytics_payload.get('subject'), json.dumps(analytics_payload))
