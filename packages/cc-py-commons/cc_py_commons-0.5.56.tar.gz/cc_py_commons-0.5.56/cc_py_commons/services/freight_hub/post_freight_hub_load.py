import os
import requests

from cc_py_commons.utils.logger_v2 import logger

FREIGHT_HUB_URL = os.environ.get('FREIGHT_HUB_URL')
FREIGHT_HUB_TOKEN = os.environ.get("FREIGHT_HUB_TOKEN")

def execute(load):
  url = f"{FREIGHT_HUB_URL}/freight"
  token = f"Bearer {FREIGHT_HUB_TOKEN}"
  headers = {
    "Authorization": token
  }
  
  logger.debug(f"post_freight_hub_load: Posting to freight-hub: {url}, {headers}, {load}")
  return requests.post(url, json=load, headers=headers)
