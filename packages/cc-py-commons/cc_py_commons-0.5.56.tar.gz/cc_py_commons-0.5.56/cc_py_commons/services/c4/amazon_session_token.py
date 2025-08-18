import requests

from cc_py_commons.utils.logger_v2 import logger
from .constants import C4_API_AUTH_TOKEN, C4_API_URL


def execute():
	url = f"{C4_API_URL}/amazonFreight/sessionToken"
	token = f"Bearer {C4_API_AUTH_TOKEN}"
	headers = {
		"Authorization": token
	}
	response = requests.get(url, headers=headers)

	if response.status_code != 200:
		logger.warning(f"Request to get Amazon session token failed with status code: {response.status_code}")
		return None

	return response.json()
