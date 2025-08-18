import os

import requests

from cc_py_commons.utils import json_logger

LOCATION_API_URL = os.environ.get('LOCATION_API_URL')
LOCATION_API_TOKEN = os.environ.get('LOCATION_API_TOKEN')


def execute(origin_latitude, origin_longitude, destination_latitude, destination_longitude, with_duration=False):
	url = f'{LOCATION_API_URL}/distance?originLatitude={origin_latitude}&originLongitude={origin_longitude}&destinationLatitude={destination_latitude}&destinationLongitude={destination_longitude}'
	if with_duration:
		url = f'{url}&withDuration=true'
	token = f"Bearer {LOCATION_API_TOKEN}"
	headers = {
		"Authorization": token
	}
	json_logger.debug(None, 'Get distance url', url=url)
	response = requests.get(url, headers=headers)
	if response.status_code != 200:
		json_logger.warning(None, 'Request to get distance failed', response_status_code=response.status_code,
							response_text=response.text)
		return None
	if with_duration:
		return response.json()
	else:
		return {'distance': response.json()}
