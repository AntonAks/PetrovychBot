import requests
import json
import ast
import settings
from datetime import datetime, timedelta
from pymongo import MongoClient


client = MongoClient(settings.MONGO_DB)
db = client.petrovych_db
currency_rates_collection = db["currency_rates"]
messages_collection = db["chat_messages"]


def store_currency_rates():

    mongo_cursor = currency_rates_collection.find().limit(1).sort([('$natural', -1)])

    try:
        last_rates = list(mongo_cursor)[0]
        db_check = datetime.now() - last_rates['Date'] > timedelta(seconds=settings.CURRENCY_RELOAD_TIME)
    except IndexError:
        db_check = True

    if db_check:

        privat_resp = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')
        nbu_resp = requests.get('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json')
        mono_resp = requests.get('https://api.monobank.ua/bank/currency')

        privat_response_text = json.loads(privat_resp.text)
        nbu_response_text = json.loads(nbu_resp.text)
        mono_response_text = json.loads(mono_resp.text)

        currency_rates_collection.insert_one({
            "Date": datetime.now(),
            "Rates": {
                "PRIVAT": privat_response_text,
                "MONO": mono_response_text,
                "NBU": nbu_response_text
            }
        })


def store_message(message, correct=True):
    message_dict = json.loads(str(message))
    messages_collection.insert_one({
        "correct": correct,
        "message": message_dict
    })
