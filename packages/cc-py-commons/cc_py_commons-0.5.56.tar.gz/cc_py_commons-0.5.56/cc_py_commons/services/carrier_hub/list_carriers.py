import json
import requests

from cc_py_commons.config.env import app_config
from cc_py_commons.utils.logger_v2 import logger

def execute(filters, page=0, size=20, max_size=False):
	"""
	Fetch a list of matching carriers from carrier-hub.
	Always returns a list.
	"""
	carriers = []
	uri = app_config.CARRIER_HUB_URL + '/carriers'
	query_params = {
		'page': page,
		'size': size,
		'maxSize': max_size
	}
	request_headers = {
		'Authorization': 'Bearer ' + app_config.CARRIER_HUB_AUTH_TOKEN,
		'Content-Type': 'application/json'
	}

	try:
		payload = {'filter': filters}
		response = requests.post(uri, json.dumps(payload), params=query_params, headers=request_headers)

		if response.status_code == 200:
			carriers = response.json()['content']
			logger.debug(f"For filters: {filters} number of carriers found: {len(carriers)}")
		else:
			logger.warning(f"Failed to lookup carriers: {response.text}")
	except Exception as e:
		logger.error(f'Error while listing carriers {e}')
		carriers = []

	return carriers
