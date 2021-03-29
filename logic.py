import logging
import settings
from aiogram import Bot, Dispatcher, types
from midlwares import AccessMiddleware
from bot_commands import kurs, help, aphorism, news
from free_talk import short_talk
from data_collector import store_message
from telegram_bot_pagination import InlineKeyboardPaginator

# bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot)
# dp.middleware.setup(AccessMiddleware(settings.ACCESS_ID))


async def get_news(chat_id, page=0):
    news_list = news.get_news()

    if page < 0:
        page = 0

    navigation_btns = types.InlineKeyboardMarkup()

    forward = types.InlineKeyboardButton(text='>>', callback_data='>>')
    backward = types.InlineKeyboardButton(text='<<', callback_data='<<')

    navigation_btns.row(backward, forward)

    try:
        await bot.send_message(chat_id, f"{page}/{len(news_list)-1}:\n{news_list[page]}", reply_markup=navigation_btns)
    except IndexError:
        await bot.send_message(chat_id, "На этом пока все :)")


@dp.message_handler(commands=['start', 'help'])
async def send_help(message: types.Message):
    await message.answer(help.answer_help_command)


@dp.message_handler(commands=['news'])
async def send_help(message: types.Message, page=0):
    await get_news(message["chat"]["id"], page)


@dp.callback_query_handler(lambda c: c.data in ['<<', '>>'])
async def characters_page_callback(call):
    page = int(call.message.text.split('/')[0])

    if call['data'] == ">>":
        page = page + 1
        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        await get_news(call["message"]["chat"]["id"], page)

    if call['data'] == "<<":
        page = page - 1

        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        await get_news(call["message"]["chat"]["id"], page)


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
    keyboard.row(usd_rates, eur_rates, rub_rates)

    await bot.send_message(message["chat"]["id"], "Прошу выбрать валюту", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['USD', 'EUR', 'RUB'])
async def callback_worker(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates(call['data']))


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
