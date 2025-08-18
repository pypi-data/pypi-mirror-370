from cc_py_commons.db import connection as db_connection


def execute(table_name):
	conn = None
	try:
		conn = db_connection.get()
		cursor = conn.cursor()
		sql_query = f'DROP TABLE IF EXISTS {table_name}'
		cursor.execute(sql_query)
		conn.commit()
	finally:
		db_connection.close(conn)
