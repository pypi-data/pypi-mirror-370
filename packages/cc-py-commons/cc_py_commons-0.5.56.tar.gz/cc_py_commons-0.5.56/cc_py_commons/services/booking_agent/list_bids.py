import os

import requests
from dateutil.parser import parse

from cc_py_commons.bids.bid_schema import BidSchema
from cc_py_commons.utils import json_logger

BOOKING_AGENT_URL = os.environ.get('BOOKING_AGENT_URL')
BOOKING_AGENT_TOKEN = os.environ.get("BOOKING_AGENT_TOKEN")


def execute(account_id, filters_dict):
	url = f"{BOOKING_AGENT_URL}/bid/match"
	token = f"Bearer {BOOKING_AGENT_TOKEN}"
	headers = {
		"Authorization": token
	}
	json_logger.debug(account_id, f"Requesting bids from booking-agent", url=url, filters=filters_dict)
	response = requests.get(url, headers=headers, params=filters_dict)
	bids = []
	if response.status_code == 200:
		bids = response.json()['content']
		for bid in bids:
			bid['pickupDate'] = parse(bid['pickupDate']).strftime('%Y-%m-%d')
			bid['deliveryDate'] = parse(bid['deliveryDate']).strftime('%Y-%m-%d')
			if bid.get('inviteEmailedAt'):
				bid['inviteEmailedAt'] = parse(bid['inviteEmailedAt']).isoformat()
			for bid_history in bid.get('bidHistories', []):
				bid_history['pickupDate'] = parse(bid_history['pickupDate']).strftime('%Y-%m-%d')
				bid_history['deliveryDate'] = parse(bid_history['deliveryDate']).strftime('%Y-%m-%d')
		bids = BidSchema().load(bids, many=True)
	return bids
