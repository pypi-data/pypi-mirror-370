import requests

from cc_py_commons.utils.logger_v2 import logger
from .constants import BOOKING_AGENT_TOKEN, BOOKING_AGENT_URL


def execute(bid_id):
  url = f"{BOOKING_AGENT_URL}/quote/-/bid/{bid_id}/accept"
  token = f"Bearer {BOOKING_AGENT_TOKEN}"
  headers = {
    "Authorization": token
  }

  logger.debug(f"Accepting bid {bid_id} in booking-agent: {url}, {headers}")
  response = requests.post(url, headers=headers)

  if response.status_code == 200:
    logger.debug(f"Successfully accepted the bid: {bid_id}")
    return response.json()
  else:
    logger.warning(f'Failed to accept bid {response.status_code}:{response.text}')

  return None
