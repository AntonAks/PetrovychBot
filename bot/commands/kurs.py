import settings
from multilang import currency_exchange_lang as cur_lang_dict
from db import currency_rates_collection

#
currency_codes = {"USD": 840,
                  "EUR": 978,
                  "RUB": 643,
                  "UAH": 980}


def get_currency_rates(currency: str) -> str:

    mongo_cursor = currency_rates_collection.find().limit(1).sort([('$natural', -1)])
    last_rates = list(mongo_cursor)[0]

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


def __parse_message(message, language):

    cur1 = None
    cur2 = None
    cur_mapping = cur_lang_dict['cur_mapping'][language]

    splited = message.split(' ')

    try:
        value = float(splited[1].replace(',', '.'))
    except ValueError:
        value = None

    for key in cur_mapping.keys():
        if splited[2].lower() in cur_mapping[key]:
            cur1 = key

    for key in cur_mapping.keys():
        if splited[4].lower() in cur_mapping[key]:
            cur2 = key

    return value, cur1, cur2


def exchange_currency(msg, language):
    try:
        value, cur1, cur2,  = __parse_message(msg, language)
    except IndexError:
        return cur_lang_dict['index_error'][language]

    result_value = 0

    if None in [cur1, cur2, value]:
        return cur_lang_dict['text_error'][language]

    if cur1 == 'RUB' and cur2 != 'UAH':
        return cur_lang_dict['rub_error'][language]
    elif cur2 == 'RUB' and cur1 != 'UAH':
        return cur_lang_dict['rub_error'][language]

    if cur1 == cur2:
        return f"{value} {cur2}"

    mongo_cursor = currency_rates_collection.find().limit(1).sort([('$natural', -1)])
    last_rates = list(mongo_cursor)[0]

    for i in last_rates['Rates']['MONO']:
        if i['currencyCodeA'] == currency_codes[cur1] and i['currencyCodeB'] == currency_codes[cur2]:
            result_value = i['rateBuy'] * value
        elif i['currencyCodeA'] == currency_codes[cur2] and i['currencyCodeB'] == currency_codes[cur1]:
            result_value = value / i['rateSell']

    return f"{result_value.__round__(4)} {cur2}"
