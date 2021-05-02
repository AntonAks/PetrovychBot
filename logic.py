import logging
import settings
from aiogram import Bot, Dispatcher, types
from midlwares import AccessMiddleware
from bot_commands import kurs, help, aphorism, news, reminder
from free_talk import short_talk
from data_collector import store_message


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


@dp.message_handler(commands=['reminder'])
async def send_help(message: types.Message):
    msg = "Введите дату и событие/действие о котором следует напомнить \n" \
          "\n" \
          "Пример 1: Петрович, напомни завтра в 14:00 вынести мусор \n" \
          "Пример 2: Петрович, напомни 14.10.2021 в 08:50 позвонить в банк \n"

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
        if len(reminders_str) > 0:
            await bot.send_message(call["message"]["chat"]["id"], reminders_str, reply_markup=keyboard)
        else:
            await bot.send_message(call["message"]["chat"]["id"], 'Список пуст :(')

    if call['data'] == 'delete_reminders':

        keyboard = types.InlineKeyboardMarkup()
        confirm_yes_btn = types.InlineKeyboardButton(text='Да, все удалить',
                                                     callback_data='delete_reminders_confirm_yes')
        confirm_no_btn = types.InlineKeyboardButton(text='Я передумал',
                                                    callback_data='delete_reminders_confirm_no')

        keyboard.row(confirm_yes_btn, confirm_no_btn)
        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        await bot.send_message(call["message"]["chat"]["id"], "Вы уверены?", reply_markup=keyboard)

    if call['data'] == 'delete_reminders_confirm_yes':
        reminder.del_reminders(call['from']['id'])
        await bot.send_message(call["message"]["chat"]["id"], "Удалено")

    if call['data'] == 'delete_reminders_confirm_no':
        await bot.send_message(call["message"]["chat"]["id"], "Правильное решени")


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

    exchange_btn = types.InlineKeyboardButton(text='Конвертер валют', callback_data='Exchange')

    keyboard.row(usd_rates, eur_rates, rub_rates)
    keyboard.add(exchange_btn)
    await bot.send_message(message["chat"]["id"], "Прошу выбрать валюту", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['USD', 'EUR', 'RUB'])
async def callback_worker(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates(call['data']))


@dp.callback_query_handler(lambda c: c.data == 'Exchange')
async def callback_worker(call: types.CallbackQuery):
    msg = "Введите слово 'Обмен или Меняю' и после, через пробел сумму, название валюты продажи, и валюту покупки. \n" \
          "\n" \
          "Пример 1: Обмен 45.6 USD на UAH \n" \
          "Пример 2: Меняю 50 долларов на евро \n"

    await bot.send_message(call["message"]["chat"]["id"], msg)


@dp.message_handler()
async def message_handler(message: types.Message):

    answer = short_talk.short_talk_answer(message)
    if answer:
        await message.answer(answer[0])
        store_message(message, answer[1])
    else:
        store_message(message)

logging.basicConfig(level=logging.INFO)
