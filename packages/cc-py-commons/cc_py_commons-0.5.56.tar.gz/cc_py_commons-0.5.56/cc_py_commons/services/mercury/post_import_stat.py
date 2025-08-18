import os
import requests

MERCURY_URL = os.environ.get("MERCURY_URL")
MERCURY_TOKEN = os.environ.get("MERCURY_TOKEN")

from cc_py_commons.utils.logger_v2 import logger


def execute(import_stat):
  url = f"{MERCURY_URL}/importStats"
  token = f"Bearer {MERCURY_TOKEN}"
  headers = {
    "Authorization": token
  }
  response = requests.post(url, json=import_stat, headers=headers)
  if response.status_code not in [200, 201]:
    logger.error(f"Failed to post import stat {import_stat} - {response.status_code}:{response.text}")
    return None
  else:
    return response.json()
