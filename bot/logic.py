import logging
import settings
import commands
from commands import keyboards
from timezonefinder import TimezoneFinder
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types
from commands import news, kurs, aphorism, reminder, admin, oracul
from nlp_engine import short_talk
from db import User
from midlwares import BlackListMiddleware, AdminAccessMiddleware

# bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AdminAccessMiddleware(settings.ACCESS_ID))
dp.middleware.setup(BlackListMiddleware())


""" Commands & Logic"""


# START
@dp.message_handler(commands=['start'])
async def _start_command(message: types.Message):

    user = User(message.from_user.id)
    try:
        user.user_name = message.from_user.username
    except Exception:
        user.user_name = None
    user.add_user()
    await message.answer(commands.start_, reply_markup=keyboards.location_keyboard(message))


# MENU
@dp.message_handler(Text(equals="Меню"))
@dp.message_handler(commands=['menu', 'help'])
async def _menu_command(message: types.Message):
    await message.answer('Сделайте всой выбор', reply_markup=keyboards.main_keyboard())


# GET USERS (Admin)
@dp.message_handler(commands=['getusers'])
async def _users_command(message: types.Message):
    await message.answer(admin.get_users())


# NEWS
@dp.callback_query_handler(lambda c: c.data in ['news'])
async def with_puree(message: types.Message, page=1):
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    await get_news_from_db(message["message"]["chat"]["id"], page)


@dp.callback_query_handler(lambda c: c.data in ['<<', '>>'])
async def news_page_callback(call):
    page = int(call.message.text.split('/')[0])

    if call['data'] == ">>":
        page = page + 1
        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        await get_news_from_db(call["message"]["chat"]["id"], page)

    if call['data'] == "<<":
        page = page - 1

        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        await get_news_from_db(call["message"]["chat"]["id"], page)


async def get_news_from_db(chat_id, page=1):
    news_list = news.get_news()

    if page < 1:
        page = 1

    navigation_btns = types.InlineKeyboardMarkup()

    forward = types.InlineKeyboardButton(text='>>', callback_data='>>')
    backward = types.InlineKeyboardButton(text='<<', callback_data='<<')

    navigation_btns.row(backward, forward)

    try:
        await bot.send_message(chat_id, f"{page}/{len(news_list)}:\n{news_list[page-1]}", reply_markup=navigation_btns)
    except IndexError:
        await bot.send_message(chat_id, "На этом пока все :)")


# CURRENCY / EXCHANGE
@dp.callback_query_handler(lambda c: c.data in ['kurs'])
async def currency_command(message: types.Message):
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    keyboard = types.InlineKeyboardMarkup()

    usd_rates = types.InlineKeyboardButton(text='USD', callback_data='USD')
    eur_rates = types.InlineKeyboardButton(text='EUR', callback_data='EUR')
    rub_rates = types.InlineKeyboardButton(text='RUB', callback_data='RUB')

    exchange_btn = types.InlineKeyboardButton(text='Конвертер валют', callback_data='Exchange')

    keyboard.row(usd_rates, eur_rates, rub_rates)
    keyboard.add(exchange_btn)
    await bot.send_message(message["message"]["chat"]["id"], "Выберите валюту", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['USD', 'EUR', 'RUB'])
async def currency_callback(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates(call['data']))


@dp.callback_query_handler(lambda c: c.data == 'Exchange')
async def exchange_callback(call: types.CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = "Введите слово 'Обмен или Меняю' и после, через пробел сумму, название валюты продажи, и валюту покупки. \n" \
          "\n" \
          "Пример 1: Обмен 45.6 USD на UAH \n" \
          "Пример 2: Меняю 50 долларов на евро \n"

    await bot.send_message(call["message"]["chat"]["id"], msg)


# APHORISM
@dp.message_handler(commands=['aphorism'])
async def _users_command(message: types.Message):
    await bot.delete_message(message["chat"]["id"], message["message_id"])
    aphorism_answer = aphorism.get_aphorism()
    await message.answer(aphorism_answer)


@dp.callback_query_handler(lambda c: c.data in ['aphorism'])
async def aphorism_command(message: types.Message):
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    aphorism_answer = aphorism.get_aphorism()
    await bot.send_message(message["message"]["chat"]["id"], aphorism_answer)


# REMINDERS
@dp.callback_query_handler(lambda c: c.data in ['reminder'])
async def reminder_command(message: types.Message):
    msg = "Введите дату и событие/действие о котором следует напомнить \n" \
          "\n" \
          "Пример 1: Напомни завтра в 14:00 вынести мусор \n" \
          "Пример 2: Напомни 14.10.2021 в 08:50 позвонить в банк \n"

    keyboard = types.InlineKeyboardMarkup()
    saved_reminders_btn = types.InlineKeyboardButton(text='Сохраненные напоминания',
                                                     callback_data='show_reminders')

    keyboard.add(saved_reminders_btn)

    await bot.send_message(message["message"]["chat"]["id"], msg, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['show_reminders',
                                                'delete_reminders',
                                                'delete_reminders_confirm_yes',
                                                'delete_reminders_confirm_no'])
async def reminder_callback(call: types.CallbackQuery):
    if call['data'] == 'show_reminders':
        keyboard = types.InlineKeyboardMarkup()
        delete_reminders_btn = types.InlineKeyboardButton(text='Удаление напоминаний',
                                                          callback_data='delete_reminders')
        keyboard.add(delete_reminders_btn)

        reminders_str = reminder.get_reminders(call['from']['id'])
        await bot.delete_message(call.message.chat.id, call.message.message_id)
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
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call["from"]["id"], "Вы уверены?", reply_markup=keyboard)

    if call['data'] == 'delete_reminders_confirm_yes':
        reminder.del_reminders(call['from']['id'])
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call["from"]["id"], "Удалено")

    if call['data'] == 'delete_reminders_confirm_no':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call["from"]["id"], "Правильное решение")


# ORACUL
@dp.callback_query_handler(lambda c: c.data in ['oracul'])
async def with_puree(message: types.Message):
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    await bot.send_message(message["message"]["chat"]["id"], oracul.get_prediction())


# GET LOCATION
@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    tzf = TimezoneFinder()
    user = User(message.from_user.id)
    time_zone = tzf.timezone_at(lng=message.location.longitude, lat=message.location.latitude)
    user.update_timezone(time_zone)
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    await message.answer('Спасибо. Часовой пояс обновлён.')


# COMMON MESSAGE HANDLER
@dp.message_handler()
async def message_handler(message: types.Message):
    answer = short_talk.short_talk_answer(message=message)
    if answer:
        await message.answer(answer)

logging.basicConfig(level=logging.INFO)
