import logging
import settings
from aiogram import Bot, Dispatcher, types
from midlwares import AccessMiddleware
from bot_commands import kurs, help, aphorism
from free_talk import short_talk
from data_collector import store_message

# bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot)
# dp.middleware.setup(AccessMiddleware(settings.ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_help(message: types.Message):
    await message.answer(help.answer_help_command)


@dp.message_handler(commands=['aphorism'])
async def send_aphorism(message: types.Message):
    aphorism_answer = aphorism.get_aphorism()
    await message.answer(aphorism_answer)


@dp.message_handler(commands=['kurs'])
async def send_about(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()

    usd_rates = types.InlineKeyboardButton(text='USD', callback_data='USD')
    eur_rates = types.InlineKeyboardButton(text='EUR', callback_data='EUR')
    rub_rates = types.InlineKeyboardButton(text='RUB', callback_data='RUB')

    keyboard.add(usd_rates)
    keyboard.add(eur_rates)
    keyboard.add(rub_rates)

    await bot.send_message(message["chat"]["id"], "Прошу выбрать валюту", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'USD')
async def callback_worker_1(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates('USD'))


@dp.callback_query_handler(lambda c: c.data == 'EUR')
async def callback_worker_2(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates('EUR'))


@dp.callback_query_handler(lambda c: c.data == 'RUB')
async def callback_worker_2(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates('RUB'))


@dp.message_handler()
async def message_handler(message: types.Message):
    text = message['text']
    answer = short_talk.short_talk_answer(text)
    if answer:
        await message.answer(answer[0])
        store_message(message, answer[1])
    else:
        store_message(message)

logging.basicConfig(level=logging.INFO)
