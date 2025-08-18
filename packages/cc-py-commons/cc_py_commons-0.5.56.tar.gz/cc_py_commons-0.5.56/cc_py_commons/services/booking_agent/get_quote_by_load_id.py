import requests

from cc_py_commons.utils import json_logger
from .constants import BOOKING_AGENT_TOKEN, BOOKING_AGENT_URL


def execute(load_id):
	url = f"{BOOKING_AGENT_URL}/quote/by/loadId/{load_id}"
	booking_agent_headers = {
		"Authorization": f"Bearer {BOOKING_AGENT_TOKEN}",
		"Content-Type": "application/json"
	}
	response = requests.get(url, headers=booking_agent_headers)
	if response.status_code == 200:
		return response.json()
	else:
		json_logger.warning(None, 'Failed to get quote from Booking Agent',
							status_code=response.status_code, load_id=str(load_id))
		return None
