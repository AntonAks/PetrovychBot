from db import news_collection


def get_news():

    mongo_cursor = news_collection.find().limit(1).sort([('$natural', -1)])

    try:
        last_news = list(mongo_cursor)[0]
        result = last_news['liga_news']['post_urls'][:5] + \
                 last_news['kor_news_world']['post_urls'][:5] + \
                 last_news['ain_news_it']['post_urls'][:5] + \
                 last_news['euro_news_world']['post_urls'][:5] + \
                 last_news['dou_news_it']['post_urls'][:5]
    except TypeError:
        last_news = list(mongo_cursor)[1]
        result = last_news['liga_news']['post_urls'][:5] + \
                 last_news['kor_news_world']['post_urls'][:5] + \
                 last_news['ain_news_it']['post_urls'][:5] + \
                 last_news['euro_news_world']['post_urls'][:5] + \
                 last_news['dou_news_it']['post_urls'][:5]

    return result
