import time
import settings
from aiogram import executor
from multiprocessing.context import Process
from logic import bot, dp
from data_collector import store_currency_rates


async def on_shutdown(dp):
    await bot.send_message(settings.ACCESS_ID, "Пока!")
    await bot.close()


async def on_startup(dp):
    await bot.send_message(settings.ACCESS_ID, "Привет, я Петрович!")


def start_process():
    p1 = Process(target=ParallelProcess.start_schedule, args=())
    p1.start()


class ParallelProcess:
    @staticmethod
    def start_schedule():
        # schedule.every().day.at("11:02").do(P_schedule.send_message1)
        # schedule.every(1).minutes.do(P_schedule.send_message2)
        while True:
            store_currency_rates()
            time.sleep(settings.CURRENCY_RELOAD_TIME)


if __name__ == '__main__':
    start_process()
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    except Exception as e:
        print(e)
