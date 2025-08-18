import os
import requests

from cc_py_commons.utils.logger_v2 import logger

GEOCODE_API_URL = os.environ.get('GEOCODE_API_URL')
GEOCODE_API_TOKEN = os.environ.get('GEOCODE_API_TOKEN')


def execute(city, state, zipcode):
	url = f'{GEOCODE_API_URL}?city={city}&state={state}'
	if zipcode:
		url = f'{url}&zip={zipcode}'
	token = f"Bearer {GEOCODE_API_TOKEN}"
	headers = {
		"Authorization": token
	}
	logger.debug(f"Geocoding location: URL: {url}, Headers: {headers}")

	response = requests.get(url, headers=headers)

	if response.status_code != 200:
		logger.warning(f"Request to geocode location failed with status code: {response.status_code}")
		return None

	return response.json()
