import json
import traceback

from cc_py_commons.config.env import app_config
from cc_py_commons.config.web_socket_action import WebSocketAction
from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils import json_logger


def execute(action, user_id, account_id, payload):
	if not action or not account_id or not payload:
		json_logger.warning(account_id, 'Missing required parameters')
		return None
	valid_actions = [WebSocketAction.BROADCAST_TO_USER, WebSocketAction.BROADCAST_TO_ACCOUNT]
	if action not in valid_actions:
		json_logger.warning(account_id, f'Invalid action. Should be one of {valid_actions}')
		return None
	web_socket_auth_token = app_config.WEB_SOCKET_AUTH_TOKEN
	if not web_socket_auth_token:
		json_logger.warning(account_id, 'Missing WEB_SOCKET_AUTH_TOKEN')
		return None
	try:
		message = {
			'authKey': web_socket_auth_token,
			'action': action,
			'userId': user_id,
			'accountId': account_id,
			'payload': payload
		}
		sns_service = SnsService()
		sns_service.send(app_config.WEB_SOCKET_SNS_TOPIC_ARN, 'web-socket-message', json.dumps(message))
		successful_message = 'Successfully sent the notification'
		json_logger.info(account_id, successful_message)
		return successful_message
	except Exception as e:
		json_logger.error(account_id, 'Failed to send web socket notification', error=str(e),
						  stacktrace=traceback.format_exc())
	return None
