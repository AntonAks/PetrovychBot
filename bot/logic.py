import logging
import settings
from aiogram import Bot, Dispatcher, types
import commands
from commands import news, kurs, aphorism, reminder
from nlp_engine import short_talk
from db import store_message
from midlwares import AccessMiddleware

# bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot)
# dp.middleware.setup(AccessMiddleware(settings.ACCESS_ID))


async def __del_message(call):
    await bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )


async def __del_message2(message):
    await bot.delete_message(
        message.chat.id,
        message.message_id
    )


@dp.message_handler(commands=['start', 'help'])
async def send_help(message: types.Message):
    await message.answer(commands.start)


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


@dp.message_handler(commands=['kurs'])
async def send_about(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()

    usd_rates = types.InlineKeyboardButton(text='USD', callback_data='USD')
    eur_rates = types.InlineKeyboardButton(text='EUR', callback_data='EUR')
    rub_rates = types.InlineKeyboardButton(text='RUB', callback_data='RUB')

    keyboard.add(usd_rates)
    keyboard.add(eur_rates)
    keyboard.add(rub_rates)

    await bot.send_message(message["chat"]["id"], "Выберите банк", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'USD')
async def callback_worker_1(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates('USD'))


@dp.callback_query_handler(lambda c: c.data == 'EUR')
async def callback_worker_2(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates('EUR'))


@dp.callback_query_handler(lambda c: c.data == 'RUB')
async def callback_worker_2(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates('RUB'))


@dp.callback_query_handler(lambda c: c.data == 'Exchange')
async def callback_worker(call: types.CallbackQuery):
    await __del_message(call)
    msg = "Введите слово 'Обмен или Меняю' и после, через пробел сумму, название валюты продажи, и валюту покупки. \n" \
          "\n" \
          "Пример 1: Обмен 45.6 USD на UAH \n" \
          "Пример 2: Меняю 50 долларов на евро \n"

    await bot.send_message(call["message"]["chat"]["id"], msg)


@dp.message_handler(commands=['aphorism'])
async def send_aphorism(message: types.Message):
    await __del_message2(message)
    aphorism_answer = aphorism.get_aphorism()
    await message.answer(aphorism_answer)


@dp.message_handler(commands=['reminder'])
async def send_help(message: types.Message):
    msg = "Введите дату и событие/действие о котором следует напомнить \n" \
          "\n" \
          "Пример 1: Напомни завтра в 14:00 вынести мусор \n" \
          "Пример 2: Напомни 14.10.2021 в 08:50 позвонить в банк \n"

    keyboard = types.InlineKeyboardMarkup()
    saved_reminders_btn = types.InlineKeyboardButton(text='Сохраненные напоминания',
                                                     callback_data='show_reminders')

    keyboard.add(saved_reminders_btn)

    await bot.send_message(message["chat"]["id"], msg, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['show_reminders',
                                                'delete_reminders',
                                                'delete_reminders_confirm_yes',
                                                'delete_reminders_confirm_no'])
async def callback_worker(call: types.CallbackQuery):
    if call['data'] == 'show_reminders':
        keyboard = types.InlineKeyboardMarkup()
        delete_reminders_btn = types.InlineKeyboardButton(text='Удаление напоминаний',
                                                          callback_data='delete_reminders')
        keyboard.add(delete_reminders_btn)

        reminders_str = reminder.get_reminders(call['from']['id'])
        await __del_message(call)
        if len(reminders_str) > 0:
            await bot.send_message(call["from"]["id"], reminders_str, reply_markup=keyboard)
        else:
            await bot.send_message(call["from"]["id"], 'Список пуст :(')

    if call['data'] == 'delete_reminders':

        keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
        confirm_yes_btn = types.InlineKeyboardButton(text='Да, удалить',
                                                     callback_data='delete_reminders_confirm_yes')
        confirm_no_btn = types.InlineKeyboardButton(text='Не удалять',
                                                    callback_data='delete_reminders_confirm_no')

        keyboard.row(confirm_yes_btn, confirm_no_btn)
        await __del_message(call)
        await bot.send_message(call["from"]["id"], "Вы уверены?", reply_markup=keyboard)

    if call['data'] == 'delete_reminders_confirm_yes':
        reminder.del_reminders(call['from']['id'])
        await __del_message(call)
        await bot.send_message(call["from"]["id"], "Удалено")

    if call['data'] == 'delete_reminders_confirm_no':
        await __del_message(call)
        await bot.send_message(call["from"]["id"], "Правильное решение")


@dp.message_handler(commands=['oracul'])
async def send_help(message: types.Message):
    msg = "Я могу заглянуть в будушее или дать совет \n" \
          "\n" \
          "Пример 1: Что меня ждет? \n" \
          "Пример 2: Укажи путь \n"

    await bot.send_message(message["chat"]["id"], msg)


@dp.message_handler()
async def message_handler(message: types.Message):
    answer = short_talk.short_talk_answer(message)
    if answer:
        await message.answer(answer)

logging.basicConfig(level=logging.INFO)
