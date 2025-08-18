import logging
import json

from cc_py_commons.utils.logger_v2 import logger

def log(level, account_id, message, **kwargs):
  ###
  # Takes log level (ERROR, WARN, DEBUG, INFO), account_id a message, and any number of named arguments 
  # and generates a JSON log entry using the V2 logger.
	# 
	# Dictionaries containing UUID attributes will cause an error
  ###
  obj = {
    'account_id': account_id,
    'message': message
  }
  obj.update(kwargs)  
  logger.log(level, json.dumps(obj))
  
def error(account_id, message, **kwargs):
  log(logging.ERROR, account_id, message, **kwargs, exec_info=1)
  
def warning(account_id, message, **kwargs):
  log(logging.WARNING, account_id, message, **kwargs)

def info(account_id, message, **kwargs):
  log(logging.INFO, account_id, message, **kwargs)
  
def debug(account_id, message, **kwargs):
  log(logging.DEBUG, account_id, message, **kwargs)	