import json
import logging
import pytz
import settings
from datetime import datetime
from pymongo import MongoClient

default_tz = str(pytz.timezone('Europe/Kiev'))

client = MongoClient(settings.MONGO_DB)
db = client.petrovych_db

currency_rates_collection = db["currency_rates"]
news_collection = db["news_collection"]
messages_collection = db["chat_messages"]
reminder_collection = db['reminder_collection']
users_collection = db['users_collection']


def store_message(message, correct=True):
    message_dict = json.loads(str(message))
    messages_collection.insert_one({
        "correct": correct,
        "message": message_dict
    })


class User:

    last_timezone = default_tz
    user_name = None
    created_at = None

    def __init__(self, user_id):

        try:
            user_dict = dict(messages_collection.find_one({"user_id": user_id}))
            self.last_timezone = user_dict['last_timezone']
            self.user_name = user_dict['user_name']
            self.created_at = user_dict['created_at']
        except Exception:
            pass

        self.user_id = user_id


    def is_user_exist(self):
        check = users_collection.find_one({"user_id": self.user_id})
        if check:
            return True
        return False

    def add_user(self):
        if not self.is_user_exist():
            users_collection.insert_one(
                {"user_id": self.user_id,
                 "user_name": self.user_name,
                 "last_timezone": self.last_timezone,
                 "created_at": datetime.now()}
            )

    def update_timezone(self, timezone):
        _id_user = users_collection.find_one({"user_id": self.user_id})
        logging.info(f'_id_user: {_id_user["_id"]}')
        users_collection.update_one({"_id": _id_user["_id"]}, {"$set": {"last_timezone": timezone}})

    def __str__(self):
        return f"user_id: {self.user_id}, name: {self.user_name}, last_timezone: {self.last_timezone}"

    def __repr__(self):
        return f"user_id: {self.user_id}, name: {self.user_name}, last_timezone: {self.last_timezone}"

    @staticmethod
    def get_all_users():
        users_collection.find()
        return list(users_collection.find())

    @staticmethod
    def get_user_name():
        pass
