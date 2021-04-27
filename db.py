import settings
from pymongo import MongoClient

client = MongoClient(settings.MONGO_DB)
db = client.petrovych_db

currency_rates_collection = db["currency_rates"]
news_collection = db["news_collection"]
messages_collection = db["chat_messages"]

