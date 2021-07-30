from db import news_collection


def get_news():

    mongo_cursor = news_collection.find().limit(1).sort([('$natural', -1)])
    last_news = list(mongo_cursor)[0]

    result = last_news['liga_news']['post_urls'][:4] + \
             last_news['kor_news_world']['post_urls'][:4] + \
             last_news['ain_news_it']['post_urls'][:4] + \
             last_news['liga_news_fin']['post_urls'][:4] + \
             last_news['euro_news_world']['post_urls'][:4] + \
             last_news['dou_news_it']['post_urls'][:4]

    return result