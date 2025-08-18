from datetime import date, datetime
from cc_py_commons.loads.load_schema import LoadSchema

def execute(freight_hub_json):
  freight_hub_json_copy = freight_hub_json.copy()

  pickup_date = freight_hub_json.get('pickupDate')
  if pickup_date:
    freight_hub_json_copy['pickupDate'] = date.fromtimestamp(int(pickup_date)/1000).isoformat()

  delivery_date = freight_hub_json.get('deliveryDate')
  if delivery_date:
    freight_hub_json_copy['deliveryDate'] = date.fromtimestamp(int(delivery_date)/1000).isoformat()

  available_time = freight_hub_json.get('availableTime')
  if available_time:
    freight_hub_json_copy['availableTime'] = datetime.fromtimestamp(int(available_time)/1000).isoformat()

  created = freight_hub_json.get('created')
  if created:
    freight_hub_json_copy['created'] = datetime.fromtimestamp(int(created)/1000).isoformat()

  invite_in_network_carriers_after = freight_hub_json.get('inviteInNetworkCarriersAfter')
  if invite_in_network_carriers_after:
    freight_hub_json_copy['inviteInNetworkCarriersAfter'] = datetime.fromtimestamp(int(invite_in_network_carriers_after)/1000).isoformat()

  invite_out_of_network_carriers_after = freight_hub_json.get('inviteOutOfNetworkCarriersAfter')
  if invite_out_of_network_carriers_after:
    freight_hub_json_copy['inviteOutOfNetworkCarriersAfter'] = datetime.fromtimestamp(int(invite_out_of_network_carriers_after)/1000).isoformat()

  return LoadSchema().load(freight_hub_json_copy)
