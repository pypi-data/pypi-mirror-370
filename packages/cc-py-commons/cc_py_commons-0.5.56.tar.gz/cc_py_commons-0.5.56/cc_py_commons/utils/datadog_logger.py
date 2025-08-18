import logging
import requests
import json
import socket
from datetime import datetime

from cc_py_commons.config.env import env_name, app_config

class DataDogLogHandler(logging.Handler):
	"""
	Logs to DataDog
	Requires DD_SITE and DD_API_KEY ENV variables
	"""
	def __init__(self):
		super().__init__() 
		self.api_key = app_config.DD_API_KEY
		self.headers = {
				'Content-Type': 'application/json',
				'DD-API-KEY': self.api_key,
		}
		self.dd_url = f"https://http-intake.logs.{app_config.DD_SITE}/api/v2/logs"
		self.hostname = socket.gethostname()

	def emit(self, record):
		try:
			message = self.format(record)
			log_entry = {
					'ddsource': 'python',
					'service': app_config.LOG_APP_NAME,
					'hostname': self.hostname,
					'ddtags': f"env:{env_name}",
					'message': message,
					'timestamp': datetime.utcnow().isoformat() + 'Z'  # UTC timestamp in ISO8601
			}
			response = requests.post(self.dd_url, headers=self.headers, data=json.dumps([log_entry]))

			if response.status_code != 200 and response.status_code != 202:
					raise Exception(f'Error posting log to DataDog: {response.text}')
		except Exception:
			self.handleError(record)
			