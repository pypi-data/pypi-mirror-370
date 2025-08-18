import os

class Config(object):
  """
  Parent configuration class.

  Add all config attributes in the parent class with a default.
  Then override as needed in the environment specific configs
  """
  AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
  AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
  ACCESS_KEY_ID=os.environ.get("ACCESS_KEY_ID")
  SECRET_ACCESS_KEY=os.environ.get("SECRET_ACCESS_KEY")
  LOG_APP_NAME= os.getenv('LOG_APP_NAME')
  LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
  GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
  PC_MILER_URL = "https://pcmiler.alk.com/apis/rest/v1.0/Service.svc/locations?postcodeFilter={0}&dataset=Current&authToken={1}"
  PC_MILER_KEY = os.getenv('PC_MILER_KEY')
  LOCATION_REDIS_URL = os.getenv('LOCATION_REDIS_URL')
  LOCATION_REDIS_PWD = os.getenv('LOCATION_REDIS_PWD')
  DISTANCE_CACHE_URL = os.getenv('DISTANCE_CACHE_URL')
  DISTANCE_CACHE_PASSWORD = os.getenv('DISTANCE_CACHE_PASSWORD')
  TIMEZONE_CACHE_URL = os.getenv('TIMEZONE_CACHE_URL')
  TIMEZONE_CACHE_PASSWORD = os.getenv('TIMEZONE_CACHE_PASSWORD')
  PC_MILER_HOURLY_LIMIT = 14000
  PC_MILER_MONTHLY_LIMIT = 300000
  PARSED_CARRIER_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:parsed-carrier-handler-test'
  PARSED_CARRIER_SNS_SUBJECT = 'parsed-carrier'
  PARSED_CARRIER_SNS_CLASS_NAME = 'com.cargochief.sdk.carrierhub.notifications.ParsedCarrierNotification'
  BOOK_LOAD_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-agent-book-load-test'
  BOOK_LOAD_SNS_SUBJECT = 'book-load'
  BOOK_LOAD_SNS_CLASS_NAME = 'com.cargochief.sdk.bookingagent.sns.BookLoadNotification'
  BOOKING_ASSISTANT_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-assistant-flow-test'
  BOOKING_ASSISTANT_SNS_SUBJECT = 'booking-assistant-flow'
  BOOKING_ASSISTANT_SNS_CLASS_NAME = 'com.cargochief.sdk.bookingagent.sns.BookingAssistantFlowNotification'
  BOOKING_ASSISTANT_QUOTE_CANCEL_SUBJECT = 'quote-cancelled'
  BOOKING_ASSISTANT_QUOTE_CANCEL_CLASS_NAME = 'com.cargochief.sdk.bookingagent.sns.QuoteCancelNotification'
  IMPORT_MOVEMENTS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:mcleod-import-movements-test'
  IMPORT_MOVEMENTS_SNS_SUBJECT = 'import-movements'
  IMPORT_MOVEMENTS_SNS_CLASS_NAME = 'com.cargochief.sdk.c4.sns.mcleod.ImportMovementsNotification'
  IMPORT_CARRIERS_SNS_SUBJECT = 'import-carriers'
  IMPORT_CARRIERS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:mcleod-import-carriers-test'
  MINIMUM_MILES_PER_DAY = int(os.getenv('MINIMUM_MILES_PER_DAY', 300))
  BOOKING_ASSISTANT_FLOW_QUEUE = 'https://sqs.us-west-1.amazonaws.com/791608169866/booking-agent-worker-test'
  BOOKING_ASSISTANT_DELAY_SECONDS=os.environ.get('BOOKING_ASSISTANT_DELAY_SECONDS', 0)
  TURVO_LOADS_BUCKET = 'turvo-loads-dev'
  ALJEX_LOADS_BUCKET = 'aljex-loads-dev'
  KNOWN_CLIENT_FILE_EXTENSIONS = {
    'surgetransportation.com': '6507',
    'simplelgx.com': '7084',
    'engaged': '7147',
    'amstanc4activecarrierlist': '7267',
    'us foods xlsextract': '7582',
    'clservicesinc.com': '7310',
    'zengistics': '7649'
  }
  BID_COUNTER_FAILURE_SNS_CLASS_NAME = 'com.cargochief.sdk.bookingagent.sns.BidCounterFailureNotification'
  BOOKING_AGENT_SNS_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-agent-sns-test'
  CARRIER_HUB_SNS_ARN = 'arn:aws:sns:us-west-1:791608169866:carrier-hub-sns-test'
  HERMES_SNS_ARN = 'arn:aws:sns:us-west-1:791608169866:hermes-sns-test'
  C4_ACCOUNTS_BUCKET = 'c4-accounts-test'
  ANALYTICS_SNS_ARN = 'arn:aws:sns:us-west-1:791608169866:analytics-test'
  WEB_SOCKET_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:websocket-dev'
  WEB_SOCKET_AUTH_TOKEN = os.getenv('WEB_SOCKET_AUTH_TOKEN')
  AUTO_INVITE_CARRIERS_SQS_QUEUE_URL = 'https://sqs.us-west-1.amazonaws.com/791608169866/auto-invite-carriers-dev'

  # Database
  DB_USERNAME = os.getenv('DB_USERNAME')
  DB_HOST = os.getenv('DB_HOST')
  DB_PORT = os.getenv('DB_PORT')
  DB_PASSWORD = os.getenv('DB_PASSWORD')
  DB_NAME = os.getenv('DB_NAME')

  # Services
  CARRIER_HUB_URL = os.environ.get('CARRIER_HUB_URL')
  CARRIER_HUB_AUTH_TOKEN = os.environ.get("CARRIER_HUB_AUTH_TOKEN")
  DD_API_KEY=os.environ.get('DD_API_KEY')
  DD_SITE=os.environ.get('DD_SITE')

class LocalConfig(Config):
  """Configurations for running and debugging locally, with a separate local database."""
  LOCATION_REDIS_URL='redis://localhost:6379'
  LOCATION_REDIS_PWD=None
  DISTANCE_CACHE_URL='redis://localhost:6379'
  DISTANCE_CACHE_PASSWORD=None
  TIMEZONE_CACHE_URL='redis://localhost:6379'
  TIMEZONE_CACHE_PASSWORD=None

class DevelopmentConfig(Config):
  """Configurations for running in dev mode, with a remote database."""
  
class StagingConfig(Config):
  """Configurations for running in dev mode, with a remote database."""
  BOOK_LOAD_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:booking-agent-book-load-staging'
  BOOKING_ASSISTANT_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:booking-assistant-flow-staging'
  IMPORT_MOVEMENTS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:mcleod-import-movements-staging'
  PARSED_CARRIER_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:mcleod-parsed-carrier-staging'
  IMPORT_CARRIERS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:mcleod-import-carriers-staging'
  BOOKING_ASSISTANT_FLOW_QUEUE='https://sqs.us-west-2.amazonaws.com/791608169866/booking-agent-worker-staging'

class ProductionConfig(Config):
  """Configurations for running in dev mode, with a remote database."""
  PARSED_CARRIER_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:parsed-carrier-handler-prod'
  BOOK_LOAD_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-agent-book-load-prod'
  BOOKING_ASSISTANT_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-assistant-flow-prod'
  IMPORT_MOVEMENTS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:mcleod-import-movements-prod'
  IMPORT_CARRIERS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:mcleod-import-carriers-prod'
  BOOKING_ASSISTANT_FLOW_QUEUE='https://sqs.us-west-1.amazonaws.com/791608169866/awseb-e-3dhx3ncwcd-stack-AWSEBWorkerQueue-129YBH2WM1TD0'
  TURVO_LOADS_BUCKET = 'turvo-loads-prod'
  ALJEX_LOADS_BUCKET = 'aljex-loads-prod'
  KNOWN_CLIENT_FILE_EXTENSIONS = {
    'surgetransportation.com': '6615',
    'simplelgx.com': '7084',
    'engaged': '7147',
    'amstanc4activecarrierlist': '7267',
    'us foods xlsextract': '7582',
    'clservicesinc.com': '7310',
    'zengistics': '7649'
  }
  BOOKING_AGENT_SNS_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-agent-sns-prod'
  CARRIER_HUB_SNS_ARN = 'arn:aws:sns:us-west-1:791608169866:carrier-hub-sns-prod'
  HERMES_SNS_ARN = 'arn:aws:sns:us-west-1:791608169866:hermes-sns-prod'
  C4_ACCOUNTS_BUCKET = 'c4-accounts-prod'
  ANALYTICS_SNS_ARN ='arn:aws:sns:us-west-1:791608169866:analytics-prod'
  WEB_SOCKET_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:websocket-prod'
  AUTO_INVITE_CARRIERS_SQS_QUEUE_URL = 'https://sqs.us-west-1.amazonaws.com/791608169866/auto-invite-carriers-prod'

config_options = {
    'local': LocalConfig,
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}

env_name = os.getenv('APP_SETTINGS')

if not env_name:
  print("warning: No APP_SETTINGS environment variable set, using development")
  env_name = 'development'

app_config = config_options[env_name]
