import os
import pandas as pd

from cc_py_commons.utils.logger_v2 import logger


def load_data(filename):
  path = os.path.join(os.getcwd(), 'test_data', 'raw', filename)
  logger.debug(f"load_data: loading from {path}")

  if (".csv" in filename.lower()):
    data = pd.read_csv(path)
  else:
    data = pd.read_excel(path)

  return data

def load_data_as_string(filename, skip_rows=0):
  path = os.path.join(os.getcwd(), 'test_data', 'raw', filename)
  logger.debug(f"load_data_as_string: loading from {path}")

  if (".csv" in filename.lower()):
    data = pd.read_csv(path)
  else:
    data = pd.read_excel(path, skiprows=skip_rows, dtype=str)

  return data

def load_data_as_string_without_headers(filename, skip_rows=0):
  path = os.path.join(os.getcwd(), 'test_data', 'raw', filename)
  logger.debug(f"load_data_as_string: loading from {path}")

  if (".csv" in filename.lower()):
    data = pd.read_csv(path, skiprows=skip_rows, header=None)
  else:
    data = pd.read_excel(path, skiprows=skip_rows, dtype=str, header=None)

  return data
