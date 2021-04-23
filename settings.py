try:
    import local_settings as s
except ImportError:
    import _local_settings as s

AWS_ACCESS_KEY_ID = s.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = s.AWS_SECRET_ACCESS_KEY
AWS_S3_BUCKET_NAME = s.AWS_S3_BUCKET_NAME

API_TOKEN = s.API_TOKEN
ACCESS_ID = s.ACCESS_ID
MONGO_DB = s.MONGO_DB
CURRENCY_RELOAD_TIME = 600  # seconds
NEWS_RELOAD_TIME = 900     # seconds
