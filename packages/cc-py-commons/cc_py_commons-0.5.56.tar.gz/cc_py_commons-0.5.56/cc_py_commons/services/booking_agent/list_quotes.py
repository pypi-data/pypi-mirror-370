import requests
import os
from dateutil.parser import parse

from cc_py_commons.utils import json_logger
from cc_py_commons.quotes.quote_schema import QuoteSchema

BOOKING_AGENT_URL = os.environ.get('BOOKING_AGENT_URL')
BOOKING_AGENT_TOKEN = os.environ.get("BOOKING_AGENT_TOKEN")


def execute(account_id, filters_dict):
	url = f"{BOOKING_AGENT_URL}/quote"
	token = f"Bearer {BOOKING_AGENT_TOKEN}"
	headers = {
		"Authorization": token
	}
	json_logger.debug(account_id, f"Requesting quotes from booking-agent", url=url, filters=filters_dict)
	response = requests.get(url, headers=headers, params=filters_dict)
	quotes = []
	if response.status_code == 200:
		quotes = response.json()['content']
		for quote in quotes:
			quote['pickupDate'] = parse(quote['pickupDate']).strftime('%Y-%m-%d')
			quote['deliveryDate'] = parse(quote['deliveryDate']).strftime('%Y-%m-%d')
		quotes = QuoteSchema().load(quotes, many=True)
	return quotes
