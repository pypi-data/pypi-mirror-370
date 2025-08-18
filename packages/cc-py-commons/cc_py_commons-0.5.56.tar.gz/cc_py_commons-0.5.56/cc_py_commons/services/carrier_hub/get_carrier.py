import requests

from cc_py_commons.config.env import app_config
from cc_py_commons.utils.logger_v2 import logger


def execute(carrier_id):
	carrier = None
	uri = app_config.CARRIER_HUB_URL + '/carrier/' + carrier_id
	request_headers = {
		'Authorization': 'Bearer ' + app_config.CARRIER_HUB_AUTH_TOKEN,
		'Content-Type': 'application/json'
	}
	try:
		response = requests.get(uri, headers=request_headers)
		if response.status_code == 200:
			carrier = response.json()
		else:
			logger.warning(f"Failed to find carrier for id: {carrier_id}")
	except Exception as e:
		logger.error(f'Error: {e} when getting carrier for id: {carrier_id}')
		carrier = None
	return carrier
