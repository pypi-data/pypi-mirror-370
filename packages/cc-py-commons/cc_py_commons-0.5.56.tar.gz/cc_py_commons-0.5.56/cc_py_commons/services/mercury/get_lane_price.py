import os
import requests

from cc_py_commons.utils.logger_v2 import logger

MERCURY_URL = os.environ.get("MERCURY_URL")
MERCURY_TOKEN = os.environ.get("MERCURY_TOKEN")


'''
	Either returns lane price data or None. 
	This does not provide error details to the consumer in case the lookup fails.
'''
def execute(params):
	url = f"{MERCURY_URL}/lanePricing"
	token = f"Bearer {MERCURY_TOKEN}"
	headers = {
		"Authorization": token
	}
	response = requests.get(url, params=params, headers=headers)

	if response.status_code != 200:
		logger.warning(
			f"Lane Pricing lookup failed for params: {params} - {response.status_code}:{response.text}")
		return None

	return response.json()

'''
	Returns a dict with data and error key. 
	data refers to the lane price data if the price was generated.
	error contains the stringified status code and text of Mercury response in case the lookup failed.
'''
def execute_v2(params):
	result = {
		'data': None,
		'error': None
	}
	url = f"{MERCURY_URL}/lanePricing"
	token = f"Bearer {MERCURY_TOKEN}"
	headers = {
		"Authorization": token
	}
	response = requests.get(url, params=params, headers=headers)

	if response.status_code != 200:
		error = f'{response.status_code}:{response.text}'
		result['error'] = error
		logger.warning(f"Lane Pricing lookup failed for params: {params} - {error}")
	else:
		result['data'] = response.json()
	return result
