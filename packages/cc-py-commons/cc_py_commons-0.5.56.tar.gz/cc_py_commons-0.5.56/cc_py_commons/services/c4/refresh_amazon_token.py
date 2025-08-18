import json
import requests

from cc_py_commons.utils.logger_v2 import logger
from .constants import C4_API_AUTH_TOKEN, C4_API_URL


def execute(account_id):
	url = f"{C4_API_URL}/amazonFreight/refreshToken/{account_id}"
	token = f"Bearer {C4_API_AUTH_TOKEN}"
	headers = {
		"Authorization": token
	}
	response = requests.get(url, headers=headers)

	if response.status_code != 200:
		logger.warning(f"Request to refresh Amazon token failed with status code: {response.status_code}")
		return None

	json_response = response.json()
	data_json_string = json_response.get('data', {}).get('data')
	return json.loads(data_json_string) if data_json_string else None
