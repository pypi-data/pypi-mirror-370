from unittest import TestCase
from unittest.mock import patch

from cc_py_commons.config.web_socket_action import WebSocketAction
from cc_py_commons.services.web_socket import send_notification
from cc_py_commons.sns.sns_service import SnsService


@patch.object(SnsService, 'send')
class TestSendNotification(TestCase):

	def test_when_required_parameters_are_missing(self, sns_service_send):
		result = send_notification.execute(WebSocketAction.BROADCAST_TO_ACCOUNT,
										   None, None, {'message': 'test'})

		self.assertIsNone(result)
		sns_service_send.assert_not_called()

	def test_invalid_action(self, sns_service_send):
		result = send_notification.execute('INVALID_ACTION',
										   None, 1234, {'message': 'test'})

		self.assertIsNone(result)
		sns_service_send.assert_not_called()

	def test_when_web_socket_token_is_missing(self, sns_service_send):
		result = send_notification.execute(WebSocketAction.BROADCAST_TO_ACCOUNT,
										   None, 1234, {'message': 'test'})

		self.assertIsNone(result)
		sns_service_send.assert_not_called()

	@patch('cc_py_commons.config.env.app_config.WEB_SOCKET_AUTH_TOKEN', 'TOKEN')
	def test_valid_request(self, sns_service_send):
		result = send_notification.execute(WebSocketAction.BROADCAST_TO_ACCOUNT,
										   None, 1234, {'message': 'test'})

		self.assertIsNotNone(result)
		sns_service_send.assert_called_once()
