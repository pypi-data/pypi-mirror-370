import requests

from cc_py_commons.utils.logger_v2 import logger
from .constants import C4_API_AUTH_TOKEN, C4_API_URL


def execute(account_id):
	url = f"{C4_API_URL}/accounts/{account_id}"
	token = f"Bearer {C4_API_AUTH_TOKEN}"
	headers = {
		"Authorization": token
	}
	logger.debug(f"Getting account: URL: {url}, Headers: {headers}")

	response = requests.get(url, headers=headers)

	if response.status_code != 200:
		logger.warning(f"Request to get account failed with status code: {response.status_code}")
		return None

	return response.json().get('data')
