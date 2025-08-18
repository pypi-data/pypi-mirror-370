import requests

from cc_py_commons.config.env import app_config
from cc_py_commons.utils.logger_v2 import logger

def execute(contact_id, payload):
	uri = app_config.CARRIER_HUB_URL + '/carrier/-/contact/' + contact_id
	headers = {
		'Authorization': 'Bearer ' + app_config.CARRIER_HUB_AUTH_TOKEN,
		'Content-Type': 'application/json'
	}
	logger.debug(f"Updating contact {contact_id} in carrier-hub: {uri} with payload: {payload}")
	response = requests.post(uri, headers=headers, json=payload)
	if response.status_code == 200:
		logger.debug(f"Successfully updated the contact: {contact_id}")
		return response.json()
	else:
		logger.warning(f'Failed to update contact {response.status_code}:{response.text}')
	return None
