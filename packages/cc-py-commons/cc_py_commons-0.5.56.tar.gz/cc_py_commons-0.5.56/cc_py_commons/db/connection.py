import psycopg2

from cc_py_commons.config.env import app_config

from cc_py_commons.utils.logger_v2 import logger

db_host = app_config.DB_HOST
db_user = app_config.DB_USERNAME
db_password = app_config.DB_PASSWORD
db_name = app_config.DB_NAME

def get():
	try:
		conn_string = f"host={db_host} user={db_user} password={db_password} dbname={db_name}"
		return psycopg2.connect(conn_string)
	except Exception as e:
		logger.error('db.get_connection: Failed with error: {e}', exc_info=True)
	
	return None

def close(connection):
	if connection:
			connection.close()
