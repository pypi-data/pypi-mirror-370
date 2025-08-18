import requests
import os
from dateutil.parser import parse

from cc_py_commons.utils.logger_v2 import logger
from cc_py_commons.quotes.quote_schema import QuoteSchema

BOOKING_AGENT_URL = os.environ.get('BOOKING_AGENT_URL')
BOOKING_AGENT_TOKEN = os.environ.get("BOOKING_AGENT_TOKEN")


def execute(quote_id):
  url = f"{BOOKING_AGENT_URL}/quote/{quote_id}"
  token = f"Bearer {BOOKING_AGENT_TOKEN}"
  headers = {
    "Authorization": token
  }

  logger.debug(f"Requesting quote {quote_id} from booking-agent: {url}, {headers}")
  response = requests.get(url, headers=headers)
  quote = None

  if response.status_code == 200:
    json = response.json()
    logger.debug(f"quote response: {json}")
    json['pickupDate'] = parse(json['pickupDate']).strftime('%Y-%m-%d')
    json['deliveryDate'] = parse(json['deliveryDate']).strftime('%Y-%m-%d')
    quote = QuoteSchema().load(json)

  logger.debug(f"quote response: {quote}")
  return quote
