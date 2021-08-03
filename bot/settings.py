API_TOKEN = ''
ACCESS_ID = 0


AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_S3_BUCKET_NAME = ''

MONGO_DB = ''

CURRENCY_RELOAD_TIME = 0  # seconds
NEWS_RELOAD_TIME = 0     # seconds

try:
    from local_settings import *
except ImportError:
    pass
