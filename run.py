import asyncio
import aioschedule
import settings
from aiogram import executor
from logic import bot, dp
from data_collector import NewsCollector, store_currency_rates


async def task_store_currency_rates():
    store_currency_rates()


async def task_collect_news():
    NewsCollector.collect_news_data()


async def scheduler():
    aioschedule.every(settings.CURRENCY_RELOAD_TIME).seconds.do(task_store_currency_rates)
    aioschedule.every(settings.NEWS_RELOAD_TIME).seconds.do(task_collect_news)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_shutdown(dp):
    await bot.send_message(settings.ACCESS_ID, "I'm dead... :(")


async def on_startup(dp):
    await bot.send_message(settings.ACCESS_ID, "Привет, я Петрович!")
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    except Exception as e:
        print(e)
