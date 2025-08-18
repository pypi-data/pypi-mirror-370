import pandas as pd
import s3fs
import boto3

from cc_py_commons.config.env import app_config
from cc_py_commons.utils.logger_v2 import logger

# Initializes s3fs to use AWS KEY/SECRET and returns URL for file
s3 = s3fs.S3FileSystem(key=app_config.ACCESS_KEY_ID, secret=app_config.SECRET_ACCESS_KEY)


def does_exist(bucket, filename):
  s3_url = get_s3_url(bucket, filename)
  return s3.exists(s3_url)

def load_data(file_name, bucket_name):
  data = pd.DataFrame()

  if not does_exist(bucket_name, file_name): 
    logger.warning(f"s3_file.load_data: Trying to load {bucket_name} and file: {file_name} but could not locate it.")
    return data

  s3_url = get_s3_url(bucket_name, file_name)
  logger.debug(f"s3_file.load_data: loading from {s3_url}")

  if (".csv" in file_name.lower()):
    data = pd.read_csv(s3_url, skipinitialspace=True)
    data.rename(columns=lambda x: x.strip().lower(), inplace=True)
  else:
    data = pd.read_excel(s3_url)

  return data

def load_data_as_string(file_name, bucket_name, skip_rows=0):
  data = pd.DataFrame()

  if not does_exist(bucket_name, file_name):
    logger.warning(f"S3 File: Trying to load {bucket_name} and file: {file_name} but could not locate it.")
    return data

  s3_url = get_s3_url(bucket_name, file_name)
  logger.debug(f"load_data_as_string: loading from {s3_url}")

  if (".csv" in file_name.lower()):
    data = pd.read_csv(s3_url, skipinitialspace=True)
    data.rename(columns=lambda x: x.strip().lower(), inplace=True)
  else:
    data = pd.read_excel(s3_url, skiprows=skip_rows, dtype=str)

  return data

def load_data_as_string_without_headers(file_name, bucket_name, skip_rows=0):
  data = pd.DataFrame()

  if not does_exist(bucket_name, file_name):
    logger.warning(f"S3 File: Trying to load {bucket_name} and file: {file_name} but could not locate it.")
    return data

  s3_url = get_s3_url(bucket_name, file_name)
  logger.debug(f"load_data_as_string_without_headers: loading from {s3_url}")

  if (".csv" in file_name.lower()):
    data = pd.read_csv(s3_url, skipinitialspace=True, skiprows=skip_rows, header=None)
    data.rename(columns=lambda x: x.strip().lower(), inplace=True)
  else:
    data = pd.read_excel(s3_url, skiprows=skip_rows, dtype=str, header=None)

  return data

def get_s3_url(bucket_name, filename):
  """Returns URL for file"""
  return f"s3://{bucket_name}/{filename}"

def write_file(bucket_name, filename, file_data, content_type=None):
  client = boto3.client('s3')
  client.put_object(Bucket=bucket_name, Key=filename, Body=file_data, ContentType=content_type)
