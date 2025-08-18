import pytz
from dateutil.parser import parse

##
# Date, Time, and DateTime handling functions.
# The dateutil library is used to have robust string parsing.
##


def parse_date_str_to_datetime(date_str):
  return parse(date_str)


def to_utc(input_datetime):
  """
  Take a datetime of any timezone and returns a datetime in UTC
  """
  return input_datetime.astimezone(pytz.UTC)


def is_same_date(date1, date2):
  return date1.strftime('%Y-%m-%d') == date2.strftime('%Y-%m-%d')


def format_datetime(datetime_object, format = None):
  """
  Takes a datetime object and returns string of the specified format
  """
  DEFAULT_FORMAT = '%Y-%m-%d %H:%M:%S'
  format = format or DEFAULT_FORMAT
  if datetime_object:
    return datetime_object.strftime(format)
