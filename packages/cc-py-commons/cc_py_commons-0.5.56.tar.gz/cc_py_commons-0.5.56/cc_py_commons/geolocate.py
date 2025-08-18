import googlemaps
import json
import traceback

from cc_py_commons.config.env import app_config
from cc_py_commons.utils.redis import location_db_conn, distance_db_conn, timezone_db_conn
from cc_py_commons.utils import json_logger
from ast import literal_eval

def get_location(city, state, zipcode, logger, reset_cache=False):
  return get_location_with_country(city, state, zipcode, None, logger, reset_cache)

def get_location_with_country(city, state, zipcode, country, logger, reset_cache=False):
  from_cache = False
  postcode = zipcode

  if postcode:
    parts = zipcode.split('-')
    postcode = parts[0] if len(parts) > 0 else zipcode

  data = None
  if not reset_cache:
    data = __get_location_from_cache(city, state, postcode, logger)

  if data:
    if data.get('country') and (not postcode or postcode == data.get('postcode')):
      from_cache = True
    else:
      logger.debug(json.dumps({
        'message': 'Found location in cache that was not a match',
        'city': city,
        'state': state,
        'zipcode': zipcode,
        'postcode': postcode,
        'country': country,
        'cache_key': __get_location_string(city, state, postcode) 
      }))
      data = None
      
  if not data:
    logger.debug(json.dumps({
      'message': 'Could not find location in cache',
      'city': city,
      'state': state,
      'postcode': zipcode,
      'country': country,
      'cache_key': __get_location_string(city, state, postcode) 
    }))
    data = __get_google_location(city, state, postcode, country, logger)

  if not data and postcode:
    from_cache = False
    data = __get_google_location(city=None, state=None, zipcode=postcode, country=None, logger=logger)

  if data and not data.get('postcode'):
    matching_location = __get_matching_location_from_cache(city, state, data.get('lat'), data.get('lng'), logger)
    if matching_location:
      data['postcode'] = matching_location.get('postcode')
    else:
      gmaps = googlemaps.Client(key=app_config.GOOGLE_API_KEY)
      response = None
      if zipcode:
          response = gmaps.geocode(zipcode)
      elif data.get('lat') and data.get('lng'):
          response = gmaps.reverse_geocode((data.get('lat'), data.get('lng')))
      post_code_data = __parse_response(response, city)
      data['postcode'] = post_code_data['postcode'] if post_code_data else None

    if data.get('postcode'):
      __cache_location(city, state, zipcode, data, logger)

  if data:
    if not from_cache:
      __cache_location(city, state, zipcode, data, logger)
  else:
    logger.debug(f"geolocate.get_location - Google returned no result for ({city}, {state}, {zipcode}, {country})")

  return data

def get_distance(origin_latitude, origin_longitude, destination_latitude, destination_longitude, logger, with_duration=False):
  if not origin_latitude or not origin_longitude or \
    not destination_latitude or not destination_longitude:
    raise Exception("Calculating distance requires both origin and destination lat/lng")

  from_cache = False
  distance_cache_key = __get_distance_cache_key(origin_latitude, origin_longitude, destination_latitude, destination_longitude)
  distance_data_dict = __get_distance_from_cache(distance_cache_key, logger)

  if distance_data_dict:
    from_cache = True
  else:
    json_logger.debug(None, 'Could not find distance from cache', origin_latitude=origin_latitude,
      origin_longitude=origin_longitude, destination_latitude=destination_latitude, destination_longitude=destination_longitude,
      with_duration=with_duration, distance_cache_key=distance_cache_key)

  missing_duration_and_is_required = (with_duration and not distance_data_dict.get('duration'))
  if not distance_data_dict or missing_duration_and_is_required:
      if missing_duration_and_is_required:
        json_logger.debug(None, 'Looking up distance from google because duration is missing in the cached data and it is required in the response',
		  origin_latitude=origin_latitude, origin_longitude=origin_longitude, destination_latitude=destination_latitude,
		  destination_longitude=destination_longitude, with_duration=with_duration, distance_cache_key=distance_cache_key)
      distance_data_dict = __get_google_distance(origin_latitude, origin_longitude, destination_latitude, destination_longitude, logger)

  if distance_data_dict:
    if not from_cache or missing_duration_and_is_required:
      json_logger.debug(None, 'Caching the distance', distance_cache_key=distance_cache_key, distance_data_dict=distance_data_dict)
      __cache_distance(distance_cache_key, distance_data_dict, logger)
  else:
    json_logger.debug(None, 'Google returned no result for distance', origin_latitude=origin_latitude,
      origin_longitude=origin_longitude, destination_latitude=destination_latitude, destination_longitude=destination_longitude,
      with_duration=with_duration, distance_cache_key=distance_cache_key)

  if distance_data_dict:
    if with_duration:
      return distance_data_dict
    else:
      return distance_data_dict.get('distance')
  return None

def get_timezone(lat,lng, logger):
  from_cache = False
  timezone = None
  try:
    timezone_cache_key = __get_timezone_cache_key(lat, lng)
    timezone = __get_timezone_from_cache(timezone_cache_key, logger)
    if timezone:
      from_cache = True

    if not timezone:
      gmaps = googlemaps.Client(key=app_config.GOOGLE_API_KEY)
      timezone = gmaps.timezone((lat,lng))

    if timezone and not from_cache:
      __cache_timezone(timezone_cache_key, timezone, logger)
  except googlemaps.exceptions.Timeout as e:
    msg = "geolocate.get_timezone - Timezone lookup failed {0}, {1}: {2}".format(lat, lng, e)
    if logger:
      logger.error(msg)
    else:
      print(msg)

  return timezone

def __get_google_distance(origin_latitude, origin_longitude, destination_latitude, destination_longitude, logger):
  distance_data = None
  try:
    gmaps = googlemaps.Client(key=app_config.GOOGLE_API_KEY)
    origins = [f'{origin_latitude} {origin_longitude}']
    destinations = [f'{destination_latitude} {destination_longitude}']
    response = gmaps.distance_matrix(origins,
                                     destinations,
                                     mode="driving",
                                     avoid='ferries',
                                     units="imperial")
    if response and response['rows'][0]['elements'][0].get('distance', None):
      distance_in_meters = response['rows'][0]['elements'][0]['distance']['value']
      distance = distance_in_meters / 1609
      duration_seconds = response['rows'][0]['elements'][0]['duration']['value']
      duration_minutes = duration_seconds / 60
      distance_data = {
        'distance': distance,
        'duration': duration_minutes
      }
  except Exception as e:
    logger.error("geolocate.__get_google_distance: Error while getting distance from google", e)
    distance_data = None
  return distance_data

def __get_google_location(city, state, zipcode, country, logger):
  try:
    if (not city or not state) and not zipcode:
      return None
    loc_str = ''
    data = None

    if city:
      loc_str = city

    if state:
      if len(loc_str) > 0:
        loc_str = loc_str + ', '

      loc_str = loc_str + state

    if zipcode:
      if len(loc_str) > 0:
        loc_str = loc_str + ' '

      loc_str = loc_str + zipcode

    if country:
      if len(loc_str) > 0:
        loc_str = loc_str + ', '

      loc_str = loc_str + country

    gmaps = googlemaps.Client(key=app_config.GOOGLE_API_KEY)
    response = gmaps.geocode(loc_str)
    
    if response:
      response = [results for results in response if 'country' not in results.get('types')]

      if len(response) > 1:
        logger.warning(f"Google returned multiple matches for {loc_str}. Selecting a single address.")
        selected_address = None
        if city and state:
          selected_address = __select_address(city=city, state=state, address_list=response)
        if not selected_address:
          logger.warning(f"Cannot select a single address from multiple for {loc_str}.")
          return None
        response = [selected_address]
      return __parse_response(response, city)
  except googlemaps.exceptions.Timeout as e:
    msg = "geolocate.__get_google_location - Location lookup timed out {0}, {1}, {2}: {3}".format(city, state, zipcode, e)

    if logger:
      logger.error(msg)
    else:
      print(msg)
  except googlemaps.exceptions.HTTPError as e:
    msg = "geolocate.__get_google_location - Location lookup failed {0}, {1}, {2}: {3}".format(city, state, zipcode, e)

    if logger:
      logger.error(msg)
    else:
      print(msg)

  return None

def __parse_response(response, city):
    if not response or len(response) == 0:
        return None
    ''' 
      Sample response of Google Maps API for address: Cincinati, OH, 45204
      {
          "address_components": [
              {
                  "long_name": "45204",
                  "short_name": "45204",
                  "types": [
                      "postal_code"
                  ]
              },
              {
                  "long_name": "Cincinnati",
                  "short_name": "Cincinnati",
                  "types": [
                      "locality",
                      "political"
                  ]
              },
              {
                  "long_name": "Hamilton County",
                  "short_name": "Hamilton County",
                  "types": [
                      "administrative_area_level_2",
                      "political"
                  ]
              },
              {
                  "long_name": "Ohio",
                  "short_name": "OH",
                  "types": [
                      "administrative_area_level_1",
                      "political"
                  ]
              },
              {
                  "long_name": "United States",
                  "short_name": "US",
                  "types": [
                      "country",
                      "political"
                  ]
              }
          ],
          "formatted_address": "Cincinnati, OH 45204, USA",
          "geometry": {
              "bounds": {
                  "northeast": {
                      "lat": 39.1251898,
                      "lng": -84.539683
                  },
                  "southwest": {
                      "lat": 39.073286,
                      "lng": -84.62870989999999
                  }
              },
              "location": {
                  "lat": 39.0930395,
                  "lng": -84.56676650000001
              },
              "location_type": "APPROXIMATE",
              "viewport": {
                  "northeast": {
                      "lat": 39.1251898,
                      "lng": -84.539683
                  },
                  "southwest": {
                      "lat": 39.073286,
                      "lng": -84.62870989999999
                  }
              }
          },
          "place_id": "ChIJjYEP0hK2QYgRTJoYykoQeqw",
          "postcode_localities": [
              "Cincinnati",
              "Queen City Square"
          ],
          "types": [
              "postal_code"
          ]
      }
    '''
    components = response[0]['address_components']
    types = response[0]['types']
    location = response[0]['geometry']['location']
    postcode_localities = response[0].get('postcode_localities', None)

    data = {'city': None, 'state': None, 'postcode': None}
    data['lat'] = location['lat']
    data['lng'] = location['lng']

    # when checking the response for a zipcode verify the city name is in the list of localities
    if 'postal_code' in types and postcode_localities and city:
        matches = [l for l in components if (
            'postal_localities' in l.get('types') and
            (l.short_name.lower() == city.lower() or l.long_name.lower() == city.lower())
        )]
        city_present_in_postcode_localities = (city in postcode_localities)

        if not matches and not city_present_in_postcode_localities:
            return None

    for component in components:
        if 'locality' in component['types']:
            data['city'] = component['short_name']
        elif 'administrative_area_level_1' in component['types']:
            data['state'] = component['short_name']
        elif 'postcode' in component['types'] or 'postal_code' in component['types']:
            data['postcode'] = component['short_name']
        elif 'country' in component['types']:
            data['country'] = component['short_name']

    return data

def __cache_location(city, state, zipcode, location_data, logger):
    location_string = __get_location_string(city, state, zipcode)
    location_db_conn.set(location_string, str(location_data))

def __get_location_from_cache(city, state, zipcode, logger):
  location = None

  try:
    cache_key = __get_location_string(city, state, zipcode) 
    location = location_db_conn.get(cache_key)

    if location:
      location = literal_eval(location.decode('utf-8'))
  except Exception as e:
    logger.warn("geolocate.__get_location_from_cache: Error while getting location from cache", e)
    location = None

  return location

def __get_location_string(city, state, zipcode):
  location_string = ''
  if city:
    location_string += ('_'.join(city.split(' ')))
  if state:
    location_string += f'_{state}'
  if zipcode:
    location_string += f'_{zipcode}'

  return location_string.lower()

def __cache_distance(distance_cache_key, distance_data, logger):
  distance_db_conn.set(distance_cache_key, str(distance_data))

def __get_distance_from_cache(distance_cache_key, logger):
  distance_data = {}
  try:
    cached_data = distance_db_conn.get(distance_cache_key)
    if cached_data:
      if 'duration' in str(cached_data):
        distance_data = literal_eval(cached_data.decode('utf-8'))
      else:
        distance_data['distance'] = float(cached_data)
  except Exception as e:
    json_logger.warning(None, 'Error while getting distance from cache',
    	error=str(e), stacktrace=traceback.format_exc())
    distance_data = {}
  return distance_data

def __get_distance_cache_key(origin_latitude, origin_longitude, destination_latitude, destination_longitude):
  return f'{__truncate(origin_latitude)},{__truncate(origin_longitude)}->{__truncate(destination_latitude)},{__truncate(destination_longitude)}'

def __truncate(number):
  return int(number * 1000000) / 1000000

def __cache_timezone(timezone_cache_key, timezone, logger):
  timezone_db_conn.set(timezone_cache_key, json.dumps(timezone))

def __get_timezone_from_cache(timezone_cache_key, logger):
  timezone = None
  try:
    timezone = timezone_db_conn.get(timezone_cache_key)
    if timezone:
      timezone = literal_eval(timezone.decode('utf-8'))
  except Exception as e:
    logger.warn("geolocate.__get_timezone_from_cache - Error while getting timezone from cache", e)
    timezone = None
  return timezone

def __get_timezone_cache_key(lat,lng):
  return f'{lat},{lng}'

def __select_address(city, state, address_list):
  city_and_state_list = []
  # Parse city and state from multiple addresses
  for address in address_list:
    address_components = address.get('address_components', [])
    city_and_state = {'city': None, 'state': None, 'address': address}
    for address_component in address_components:
      types = address_component.get('types', [])
      if not city_and_state['city'] and ('locality' in types or 'administrative_area_level_3' in types):
        city_and_state['city'] = address_component.get('long_name')
      elif not city_and_state['state'] and ('country' in types or 'administrative_area_level_1' in types):
        city_and_state['state'] = address_component.get('short_name')

      if city_and_state['city'] and city_and_state['state']:
        city_and_state_list.append(city_and_state)
        break

  # Select the address matching the input city and state
  for parsed_city_and_state in city_and_state_list:
    if parsed_city_and_state['city'].strip().lower() == city.strip().lower() \
      and parsed_city_and_state['state'].strip().lower() == state.strip().lower():
      return parsed_city_and_state['address']
  return None

def __get_matching_location_from_cache(city, state, lat, lng, logger):
    matching_location = None
    try:
        if city and state and lat and lng:
            key = __get_location_string(city, state, None)
            pattern = f'{key}*'
            matching_keys = location_db_conn.keys(pattern)
            if matching_keys:
                for matching_key in matching_keys:
                    location = literal_eval(location_db_conn.get(matching_key).decode('utf-8'))
                    if location.get('lat') == lat and location.get('lng') == lng and location.get('postcode'):
                        matching_location = location
                        break
    except Exception as e:
        logger.warn("geolocate.__get_matching_location_from_cache: Failed: ", e)
    return matching_location
