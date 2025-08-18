import requests

from cc_py_commons.utils import json_logger
from .constants import C4_API_AUTH_TOKEN, C4_API_URL
from . import get_account


def by_user_id(user_id):
	url = f"{C4_API_URL}/user/{user_id}/accountSettings"
	token = f"Bearer {C4_API_AUTH_TOKEN}"
	headers = {
		"Authorization": token
	}
	json_logger.debug(None, 'Getting account settings', url=url, headers=headers)
	response = requests.get(url, headers=headers)
	if response.status_code != 200:
		json_logger.warning(None, 'Request to get account settings failed', status_code=response.status_code)
		return None
	return response.json().get('data')


def by_account_id(account_id):
	account = get_account.execute(account_id)
	if account:
		return account.get('accountSettings')
	else:
		return None
