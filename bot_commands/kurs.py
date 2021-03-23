import requests
import json


def get_currency_rates():
    resp = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')
    response_text = json.loads(resp.text)

    string_currency_rates = ""

    for i in response_text:
        string_currency_rates = string_currency_rates + i['ccy'] + " >>> buy: " + i['buy'] + ": sale: " + i['sale'] + "\n"

    return string_currency_rates
