
def is_event_from_lambda_warmer(event):
	result = False
	if 'Records' not in event:
		resources = event.get('resources', [])
		if len(resources) > 0 and 'LAMBDA_WARMER' in resources[0]:
			result = True
	return result
