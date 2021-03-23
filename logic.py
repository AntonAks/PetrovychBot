import logging
from aiogram import Bot, Dispatcher, types

from midlwares import AccessMiddleware
from bot_commands import kurs, help

try:
    import local_settings as settings
except ImportError:
    import _local_settings as settings


API_TOKEN = settings.API_TOKEN
ACCESS_ID = settings.ACCESS_ID

# bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
# dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_help(message: types.Message):
    await message.answer(help.answer_help_command)


@dp.message_handler(commands=['kurs'])
async def send_about(message: types.Message):
    answer_kurs_command = kurs.get_currency_rates()
    await message.answer(answer_kurs_command)


@dp.message_handler()
async def message_handler(message: types.Message):

    print(message["chat"])
    # await message.answer(message['text'])

logging.basicConfig(level=logging.INFO)
