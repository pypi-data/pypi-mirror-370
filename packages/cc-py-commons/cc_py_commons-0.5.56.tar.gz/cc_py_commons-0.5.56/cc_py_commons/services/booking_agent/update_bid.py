import requests

from cc_py_commons.utils.logger_v2 import logger
from .constants import BOOKING_AGENT_TOKEN, BOOKING_AGENT_URL


def execute(bid_id, payload):
	url = f"{BOOKING_AGENT_URL}/quote/-/bid/{bid_id}"
	token = f"Bearer {BOOKING_AGENT_TOKEN}"
	headers = {
		"Authorization": token
	}

	logger.debug(f"Updating bid {bid_id} in booking-agent: {url} with payload: {payload}, {headers}")
	response = requests.post(url, headers=headers, json=payload)

	if response.status_code == 200:
		logger.debug(f"Successfully updated the bid: {bid_id}")
		return response.json()
	else:
		logger.warning(f'Failed to update bid {response.status_code}:{response.text}')

	return None
