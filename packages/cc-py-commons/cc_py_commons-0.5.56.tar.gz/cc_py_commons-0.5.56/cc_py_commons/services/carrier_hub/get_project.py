import traceback

import requests

from cc_py_commons.config.env import app_config
from cc_py_commons.projects.project_schema import ProjectSchema
from cc_py_commons.utils import json_logger


def execute(project_id, account_id=None):
	project = None
	uri = app_config.CARRIER_HUB_URL + '/projects/id/' + project_id
	request_headers = {
		'Authorization': 'Bearer ' + app_config.CARRIER_HUB_AUTH_TOKEN,
		'Content-Type': 'application/json'
	}
	try:
		response = requests.get(uri, headers=request_headers)
		if response.status_code == 200:
			project_json = response.json()
			project = ProjectSchema().load(project_json)
		else:
			json_logger.warning(account_id, 'Failed to find project', project_id=project_id,
								response_status_code=response.status_code, response_text=response.text)
	except Exception as e:
		json_logger.error(account_id, 'Exception when getting project',
						  project_id=project_id, error=str(e), stacktrace=traceback.format_exc())
		project = None
	return project
