import logging
import requests
import json
import settings
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from random import choice
from urllib.request import Request, urlopen
from db import currency_rates_collection, messages_collection, news_collection


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


class NewsCollector:

    @staticmethod
    def get_dou_news_it() -> dict:

        site = "https://dou.ua/lenta/"
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")
        items = soup.find_all(class_='title')

        post_names = []
        post_urls = []

        for i in items:
            a_tags = i.find_all('a')
            for a in a_tags:
                if "https://" in a.get('href'):
                    post_urls.append(a.get('href'))
                    post_names.append(str(a.getText()).strip())

        return {"post_names": post_names, "post_urls": post_urls}

    @staticmethod
    def get_itc_news_it() -> dict:

        site = "https://itc.ua/news/"
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")
        items = soup.find_all(class_='entry-title text-uppercase')

        post_names = []
        post_urls = []

        for i in items:
            a_tags = i.find_all('a')
            for a in a_tags:
                if "https://" in a.get('href'):
                    post_urls.append(a.get('href'))
                    post_names.append(str(a.getText()).strip())

        return {"post_names": post_names, "post_urls": post_urls}

    @staticmethod
    def get_liga_news() -> dict:
        site = "https://news.liga.net/ua?utm_source=ua-news"
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")
        items = soup.find_all(class_='news-nth-title')

        post_names = []
        post_urls = []

        for i in items:
            a_tags = i.find_all('a')
            for a in a_tags:
                if "https://" in a.get('href') and len(str(a.getText())) > 30:
                    post_urls.append(a.get('href'))
                    post_names.append(str(a.getText()).strip())

        return {"post_names": post_names, "post_urls": post_urls}

    @staticmethod
    def get_ain_news_it() -> dict:

        site = "https://ain.ua/post-list/"
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")
        items = soup.find_all(class_='post-link with-labels')

        post_names = []
        post_urls = []

        for i in items:
            texts = i.find_all(text=True)
            for text in texts:
                if len(text) > 3:
                    post_names.append(str(text).strip())

            if len(str(i.getText())) > 2 and "https://" in i.get('href'):
                post_urls.append(i.get('href'))

        return {"post_names": post_names, "post_urls": post_urls}

    @staticmethod
    def get_liga_news_fin() -> dict:
        site = "https://finance.liga.net/news"
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")
        items = soup.find_all(class_='news')

        post_names = []
        post_urls = []

        for i in items:
            a_tags = i.find_all('a')
            for a in a_tags:
                if "https://" in a.get('href') and len(str(a.getText())) > 2 and 'ЛІГА.' not in a.getText():
                    post_urls.append(a.get('href'))
                    post_names.append(str(a.getText()).strip())

        return {"post_names": post_names, "post_urls": post_urls}

    @staticmethod
    def get_investing_fin() -> dict:
        site = "https://ru.investing.com/news/latest-news"
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")

        leftColumn = soup.find(id='leftColumn')

        items = leftColumn.find_all(class_='textDiv')

        post_names = []
        post_urls = []

        for i in items:
            title_name = i.find_all(class_='title')[0].get('title')
            url_name = i.find_all(class_='title')[0].get('href')
            if len(title_name) > 3:
                post_names.append(title_name)
                post_urls.append('https://ru.investing.com'+url_name)

        return {"post_names": post_names, "post_urls": post_urls}

    @staticmethod
    def get_kor_news_world() -> dict:
        site = "https://korrespondent.net/world/"
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")

        unit_rubric = soup.find(class_='unit-rubric')

        items = unit_rubric.find_all(class_='article__title')

        post_names = []
        post_urls = []

        for i in items:
            a_tags = i.find_all('a')
            for a in a_tags:
                if len(str(a.getText())) > 2 and "https://" in a.get('href'):
                    post_urls.append(a.get('href'))
                    post_names.append(str(a.getText()).strip().replace("Сюжет", ""))

        return {"post_names": post_names, "post_urls": post_urls}

    @staticmethod
    def get_euro_news_world() -> dict:
        site = "https://ru.euronews.com/programs/world"
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")

        listing_articles_block = soup.find(class_='o-block-listing__articles')

        articles = listing_articles_block.find_all(class_='m-object__title__link')

        post_names = []
        post_urls = []

        for i in articles:
            post_names.append(i.getText().strip())
            post_urls.append('https://ru.euronews.com' + i.get('href'))

        return {"post_names": post_names, "post_urls": post_urls}

    @staticmethod
    def collect_news_data():
        # Deleting old object
        if news_collection.count_documents(filter={}) > 2:
            mongo_cursor = news_collection.find().limit(1).sort([('$natural', 1)])
            obj_id = list(mongo_cursor)[0]['_id']
            news_collection.delete_one({'_id': obj_id})

        call_stack = [
            NewsCollector.get_dou_news_it,
            NewsCollector.get_itc_news_it,
            NewsCollector.get_liga_news,
            NewsCollector.get_ain_news_it,
            NewsCollector.get_liga_news_fin,
            NewsCollector.get_investing_fin,
            NewsCollector.get_kor_news_world,
            NewsCollector.get_euro_news_world,
        ]

        result_list = []

        for function in call_stack:
            try:
                start = datetime.now()
                result = function()
                logging.info(f"Stored news: {function.__name__}, {datetime.now() - start}" )
            except Exception:
                result = None

            result_list.append(result)

        news_collection.insert_one(
            {"Date": datetime.now(),
             "dou_news_it": result_list[0],
             "itc_news_it": result_list[1],
             "liga_news": result_list[2],
             "ain_news_it": result_list[3],
             "liga_news_fin": result_list[4],
             "investing_fin": result_list[5],
             "kor_news_world": result_list[6],
             "euro_news_world": result_list[7],
             }
        )


class BeerCollection:
    s3 = boto3.resource('s3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                        )

    @classmethod
    def get_quantity(cls):
        predictions_list_obj = cls.s3.Object(settings.AWS_S3_BUCKET_NAME, "beer_collection.json")
        all_data = predictions_list_obj.get()['Body'].read().decode("utf-8")
        all_data = json.loads(all_data)

    @classmethod
    def prepare_beer_collection(cls):
        final_beer_dict = {
            "ABV": {
                "Non-Alcohol": {"IBU": {
                    "Low": [],
                    "Mid": [],
                    "High": []
                }},
                "Low": {"IBU": {
                    "Low": [],
                    "Mid": [],
                    "High": []
                }},
                "Mid": {"IBU": {
                    "Low": [],
                    "Mid": [],
                    "High": []
                }},
                "High": {"IBU": {
                    "Low": [],
                    "Mid": [],
                    "High": []
                }}
            }
        }

        predictions_list_obj = cls.s3.Object(settings.AWS_S3_BUCKET_NAME, "beer_collection.json")
        all_data = predictions_list_obj.get()['Body'].read().decode("utf-8")
        all_data = json.loads(all_data)

        for beer in [beer for beer in all_data if float(beer['global_rating_score']) >= 3]:

            if 2.5 <= float(beer['beer_abv']) <= 4.5:
                abv = 'Low'
            elif 4.5 < float(beer['beer_abv']) <= 6.9:
                abv = 'Mid'
            elif 6.9 < float(beer['beer_abv']):
                abv = 'High'
            else:
                abv = 'Non-Alcohol'

            if 0 <= float(beer['beer_ibu']) <= 25:
                ibu = 'Low'
            elif 25 < float(beer['beer_ibu']) <= 45:
                ibu = 'Mid'
            elif 45 < float(beer['beer_ibu']):
                ibu = 'High'
            else:
                ibu = 'Mid'

            final_beer_dict['ABV'][abv]['IBU'][ibu].append(beer)

        try:
            s3object = cls.s3.Object(settings.AWS_S3_BUCKET_NAME, 'final_beer_dict.json')
            s3object.put(Body=(bytes(json.dumps(final_beer_dict).encode('UTF-8'))))
        except ClientError as e:
            logging.error(f"Error with updating for Final Beer dictionary. {e}")

    @classmethod
    def get_random_beer(cls, abv, ibu):
        final_beer_dict = cls.s3.Object(settings.AWS_S3_BUCKET_NAME, "final_beer_dict.json")
        final_beer_dict = final_beer_dict.get()['Body'].read().decode("utf-8")
        final_beer_dict = json.loads(final_beer_dict)

        try:
            answer = choice(final_beer_dict['ABV'][abv]['IBU'][ibu])
        except KeyError:
            answer = None
        return answer

    @classmethod
    def get_non_acl_beer(cls):
        final_beer_dict = cls.s3.Object(settings.AWS_S3_BUCKET_NAME, "final_beer_dict.json")
        final_beer_dict = final_beer_dict.get()['Body'].read().decode("utf-8")
        final_beer_dict = json.loads(final_beer_dict)
        beer_dict = final_beer_dict['ABV']['Non-Alcohol']['IBU']['Low'] + \
                    final_beer_dict['ABV']['Non-Alcohol']['IBU']['High'] + \
                    final_beer_dict['ABV']['Non-Alcohol']['IBU']['Mid']
        answer = choice(beer_dict)
        return answer


if __name__ == '__main__':
    mono_resp = requests.get('https://api.monobank.ua/bank/currency')
    print(json.loads(mono_resp.text))