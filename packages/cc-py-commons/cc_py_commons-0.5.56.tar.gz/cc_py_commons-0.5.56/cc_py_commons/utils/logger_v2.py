###
# Singleton logger that removes issues with the logger being loaded multiple times and duplicating log entries
# Logs to stdout unless the ENV variable LOG_DESTINATION is present.
# Currently LOG_DESTINATION only support PAPERTRAIL
#
# Using the json_logger wrapper is preferred.
###
import os
import logging
import socket

from cc_py_commons.config.env import app_config
from cc_py_commons.utils.datadog_logger import DataDogLogHandler

PAPERTRAIL = 'PAPERTRAIL'
DATADOG = 'DATADOG'

class ContextFilter(logging.Filter):
	hostname = socket.gethostname()

	def filter(self, record):
		record.hostname = ContextFilter.hostname
		return True

class SingletonLogger:
	"""
	Creates a single instance of the logger with the given name.
	Looks for a LOG_DESTINATION ENV variable to determine where to send logs. 
	Logs to Standard Out by default. 
	Standard Out is automatically captured by DataDog and works for Lambdas.
	"""
	_instance = None

	@staticmethod
	def getInstance():
		if SingletonLogger._instance == None:
			SingletonLogger()

		return SingletonLogger._instance

	def __init__(self):
		if SingletonLogger._instance != None:
			raise Exception("This class is a singleton!")
		else:
			SingletonLogger._instance = self._config_logger()

	def _config_logger(self):
		logger = logging.getLogger(app_config.LOG_APP_NAME)
		logger.setLevel(app_config.LOG_LEVEL)
		contextFilter = ContextFilter()
		logger.addFilter(contextFilter)
		formatter = logging.Formatter('%(levelname)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
		log_destination = os.environ.get('LOG_DESTINATION')
		log_handler = logging.StreamHandler()			

		if log_destination == PAPERTRAIL:
			log_handler = logging.handlers.SysLogHandler(address=('logs3.papertrailapp.com', 10024))
		elif log_destination == DATADOG:
			log_handler = DataDogLogHandler()
			
		log_handler.setFormatter(formatter)
		
		if not logger.handlers:
			logger.addHandler(log_handler)

		logger.propagate = False
		return logger

# Usage
logger = SingletonLogger.getInstance()
