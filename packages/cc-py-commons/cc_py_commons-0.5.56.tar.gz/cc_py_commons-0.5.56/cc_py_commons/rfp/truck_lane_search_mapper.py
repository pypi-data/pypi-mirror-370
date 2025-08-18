from cc_py_commons.config.c4_account_settings import C4AccountSettings


def execute(lane_price_search, account_settings, user_id):
	return {
		'trailerTypes': [lane_price_search.get('equipment')],
		'originCity': lane_price_search.get('originCity'),
		'originState': lane_price_search.get('originState'),
		'originZip': lane_price_search.get('originPostcode'),
		'originLat': lane_price_search.get('originLatitude'),
		'originLng': lane_price_search.get('originLongitude'),
		'destCity': lane_price_search.get('destinationCity'),
		'destState': lane_price_search.get('destinationState'),
		'destZip': lane_price_search.get('destinationPostcode'),
		'destLat': lane_price_search.get('destinationLatitude'),
		'destLng': lane_price_search.get('destinationLongitude'),
		'originDeadhead': account_settings.get(C4AccountSettings.SEARCH_TRUCK_ORIGIN_DEADHEAD_LIMIT),
		'destinationDeadhead': account_settings.get(C4AccountSettings.SEARCH_TRUCK_DESTINATION_DEADHEAD_LIMIT),
		'resultCount': account_settings.get(C4AccountSettings.SEARCH_TRUCK_RESULTS_COUNT),
		'pickupDateStart': lane_price_search.get('pickupDate'),
		'pickupDateEnd': lane_price_search.get('deliveryDate'),
		'accountId': lane_price_search.get('accountId'),
		'userId': user_id,
		'userType': 'USER',
		'inNetworkCarriers': True
	}
