import settings
from pymongo import MongoClient


def get_currency_rates(currency: str) -> str:

    client = MongoClient(settings.MONGO_DB)
    db = client.petrovych_db
    currency_rates_collection = db["currency_rates"]

    mongo_cursor = currency_rates_collection.find().limit(1).sort([('$natural', -1)])
    last_rates = list(mongo_cursor)[0]

    currency_codes = {"USD": 840,
                      "EUR": 978,
                      "RUB": 643}

    string_currency_rates = "UAH to " + currency + ":" "\n"

    # PRIVAT RATES
    for i in last_rates['Rates']['PRIVAT']:
        currency_privat = currency
        if currency == "RUB":
            currency_privat = "RUR"
        if i['ccy'] == currency_privat:
            string_currency_rates = string_currency_rates + "PRIVAT >>> " + " buy: " + i['buy'] + " sale: " + i['sale'] + "\n"

    # MONO RATES
    for i in last_rates['Rates']['MONO']:
        currency_code = currency_codes[currency]
        if i['currencyCodeA'] == currency_code and i['currencyCodeB'] == 980:
            string_currency_rates = string_currency_rates + "MONO >>> " + " buy: " + str(i['rateBuy']) + " sale: " + str(i['rateSell']) + "\n"

    # NBU RATES
    for i in last_rates['Rates']['NBU']:
        if i['cc'] == currency:
            string_currency_rates = string_currency_rates + "NBU >>> " + " rate: " + str(i['rate']) + "\n"

    return string_currency_rates
