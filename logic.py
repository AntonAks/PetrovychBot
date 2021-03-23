import logging
from aiogram import Bot, Dispatcher, types

from midlwares import AccessMiddleware

try:
    import local_settings as settings
except ImportError:
    import _local_settings as settings


API_TOKEN = settings.API_TOKEN
ACCESS_ID = settings.ACCESS_ID

# bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler()
async def message_handler(message: types.Message):
    await message.answer(message['text'])

logging.basicConfig(level=logging.INFO)
