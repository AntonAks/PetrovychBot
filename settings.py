try:
    import local_settings as s
except ImportError:
    import _local_settings as s


API_TOKEN = s.API_TOKEN
ACCESS_ID = s.ACCESS_ID

MONGO_DB = "localhost:27017"
