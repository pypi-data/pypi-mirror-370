import requests

from cc_py_commons.utils.logger_v2 import logger
from .constants import BOOKING_AGENT_TOKEN, BOOKING_AGENT_URL


def execute(amazon_order_id):
  url = f"{BOOKING_AGENT_URL}/bids/list"
  token = f"Bearer {BOOKING_AGENT_TOKEN}"
  headers = {
    "Authorization": token
  }
  payload = {
    'amazonOrderIds': [amazon_order_id]
  }

  logger.debug(f"Requesting bid for amazon order {amazon_order_id} from booking-agent: {url}, {headers}")
  response = requests.post(url, headers=headers, json=payload)
  bid = None

  logger.debug(f"bid response: {response}")
  if response.status_code == 200:
    bid = response.json()

  return bid
