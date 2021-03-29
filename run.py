import time
import settings
from aiogram import executor
from multiprocessing.context import Process
from logic import bot, dp
from data_collector import NewsCollector, store_currency_rates


async def on_shutdown(dp):
    await bot.send_message(settings.ACCESS_ID, "Я умер!")
    await bot.close()


async def on_startup(dp):
    await bot.send_message(settings.ACCESS_ID, "Привет, я Петрович!")


def start_process():
    p1 = Process(target=CurrencyRatesCollector.start_parsing, args=())
    p2 = Process(target=NewsCollectorProcess.start_parsing, args=())
    p1.start()
    p2.start()


class CurrencyRatesCollector:
    @staticmethod
    def start_parsing():
        while True:
            store_currency_rates()
            time.sleep(settings.CURRENCY_RELOAD_TIME)


class NewsCollectorProcess:
    @staticmethod
    def start_parsing():
        while True:
            NewsCollector.collect_news_data()
            time.sleep(settings.NEWS_RELOAD_TIME)


if __name__ == '__main__':
    start_process()
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    except Exception as e:
        print(e)
