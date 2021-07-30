import requests
import json


def get_aphorism():
    aphorism = requests.get("http://api.forismatic.com/api/1.0/?method=getQuote&format=jsonp&jsonp=parseQuote")

    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    aphorism_text = json.loads(find_between(s=aphorism.text, first="parseQuote(", last=")"))

    answer_string = aphorism_text["quoteText"] + '\n'
    answer_string = answer_string + '\n' + f"{aphorism_text['quoteAuthor']}"

    return answer_string

