import requests
import json
import settings
from datetime import datetime
from pymongo import MongoClient


client = MongoClient(settings.MONGO_DB)
db = client.petrovych_db
currency_rates_collection = db["currency_rates"]


def store_currency_rates():

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
