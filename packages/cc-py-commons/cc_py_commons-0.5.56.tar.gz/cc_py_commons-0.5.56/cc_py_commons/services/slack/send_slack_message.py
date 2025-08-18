import json
import requests

from cc_py_commons.utils.logger_v2 import logger


def execute(channel_webhook_url, message_title, fields_list):
	'''
		sample field: {
			'title': 'Label',
			'value': 'Value'
		}
	'''
	try:
		payload = __payload(message_title, fields_list)
		logger.debug(f'slack.send_slack_message: Sending slack message: {payload} to webhook: {channel_webhook_url}')
		response = requests.post(channel_webhook_url, json.dumps(payload))
		if response.status_code == 200:
			logger.debug(f"Successfully sent message.")
		else:
			logger.warning(f"Failed to send slack message. Response from slack {response.text}")
	except Exception as e:
		logger.error(f'slack.send_slack_message: Failed with error: {e}')

def __payload(message_title, fields_list):
	fields = []
	if fields_list:
		for field in fields_list:
			fields.append({
				'title': field.get('title'),
				'value': field.get('value'),
				'short': True
      })
	payload = {
		'text': f'*{message_title}*',
		'attachments': [{
			'fields': fields
		}]
	}
	return payload
