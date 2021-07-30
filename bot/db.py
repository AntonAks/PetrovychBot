import json
from pymongo import MongoClient

MONGO_DB = "mongodb://db:27017"
client = MongoClient(MONGO_DB)
db = client.petrovych_db

currency_rates_collection = db["currency_rates"]
news_collection = db["news_collection"]
messages_collection = db["chat_messages"]
reminder_collection = db['reminder_collection']


def store_message(message, correct=True):
    message_dict = json.loads(str(message))
    messages_collection.insert_one({
        "correct": correct,
        "message": message_dict
    })
