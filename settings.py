try:
    import local_settings as s
except ImportError:
    import _local_settings as s


API_TOKEN = s.API_TOKEN
ACCESS_ID = s.ACCESS_ID
MONGO_DB = s.MONGO_DB
CURRENCY_RELOAD_TIME = 600  # seconds
NEWS_RELOAD_TIME = 900     # seconds
SHORT_TALKS = s.SHORT_TALKS
