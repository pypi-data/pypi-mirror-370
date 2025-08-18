import requests

from cc_py_commons.config.env import app_config
from cc_py_commons.utils.logger_v2 import logger

def execute(email_address_list=(), carrier_id_list=(), is_mail_receiver=False, page=0, size=20):
	"""
	Fetch a list of matching contacts from carrier-hub.
	Always returns a list.
	"""
	contacts = []
	if not email_address_list and not carrier_id_list:
		return contacts
	filtered_email_address_list = list(filter(None, email_address_list))
	email_address_string = ','.join(filtered_email_address_list) if email_address_list else ''
	uri = app_config.CARRIER_HUB_URL + '/carrier/-/contact'
	query_params = {
		'page': page,
		'size': size,
		'EMAIL_IDS': email_address_string
	}
	if is_mail_receiver:
		query_params['isMailReciever'] = is_mail_receiver
	if carrier_id_list:
		query_params['CARRIER_IDS'] = ','.join(map(str, carrier_id_list))
	request_headers = {
		'Authorization': 'Bearer ' + app_config.CARRIER_HUB_AUTH_TOKEN,
		'Content-Type': 'application/json'
	}
	try:
		response = requests.get(uri, params=query_params, headers=request_headers)
		if response.status_code == 200:
			contacts = response.json()['content']
			logger.debug(f"For filters: {query_params} number of contacts found: {len(contacts)}")
		else:
			logger.warning(f"Failed to lookup contacts: {response.text}")
	except Exception as e:
		logger.error(f'Error while listing contacts {e}')
		contacts = []

	return contacts
