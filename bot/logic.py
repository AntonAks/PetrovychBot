import logging
import settings
import commands
import multilang
from multilang import reminder_commands_lang as rcl
from commands import keyboards
from timezonefinder import TimezoneFinder
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types
from commands import news, kurs, aphorism, reminder, admin, oracul, beer
from nlp_engine import short_talk
from db import User, Chat
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
    chat = Chat(message["chat"]["id"])
    try:
        user.user_name = message.from_user.username
    except Exception:
        user.user_name = None
    user.add_user()
    await message.answer(commands.start_[chat.chat_language],
                         reply_markup=keyboards.location_keyboard(message, chat.chat_language))


# MENU
@dp.message_handler(Text(equals="Меню"))
@dp.message_handler(commands=['menu', 'help'])
async def _menu_command(message: types.Message):
    chat = Chat(message["chat"]["id"])
    await message.answer(multilang.keyboards_lang[chat.chat_language]['make_choice'],
                         reply_markup=keyboards.main_keyboard(chat.chat_language))


# GET USERS (Admin)
@dp.message_handler(commands=['getusers'])
async def _users_command(message: types.Message):
    await message.answer(admin.get_users())


# BEER
@dp.callback_query_handler(lambda c: c.data in ['beer'])
async def _beer_command(message: types.Message):
    chat = Chat(message["message"]["chat"]["id"])
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    await bot.send_message(message["message"]["chat"]["id"],
                           multilang.beer_choice_text['abv_choice'][chat.chat_language],
                           reply_markup=keyboards.beer_choice_abv(chat.chat_language))


@dp.message_handler(commands=['beer'])
async def _beer_command(message: types.Message):
    chat = Chat(message["chat"]["id"])
    await bot.delete_message(message["chat"]["id"], message["message_id"])
    await bot.send_message(message["chat"]["id"],
                           multilang.beer_choice_text['abv_choice'][chat.chat_language],
                           reply_markup=keyboards.beer_choice_abv(chat.chat_language))


@dp.callback_query_handler(lambda c: c.data in ['No Alco', 'Low', 'Mid', 'High'])
async def _beer_abv(message: types.Message):
    chat = Chat(message["message"]["chat"]["id"])
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    await bot.send_message(message["message"]["chat"]["id"],
                           multilang.beer_choice_text['ibu_choice'][chat.chat_language],
                           reply_markup=keyboards.beer_choice_ibu(message['data'], chat.chat_language))


@dp.callback_query_handler(lambda c: c.data in beer.beer_combinations_list)
async def _beer_ibu(message: types.Message):
    chat = Chat(message["message"]["chat"]["id"])

    abv, ibu = message['data'].split('-')[0], message['data'].split('-')[1]

    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    await bot.send_message(message["message"]["chat"]["id"], beer.get_beer_card(abv=abv,
                                                                                ibu=ibu,
                                                                                language=chat.chat_language),
                           parse_mode='html')


# NEWS
@dp.callback_query_handler(lambda c: c.data in ['news'])
async def _news(message: types.Message, page=1):
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
        await bot.send_message(chat_id,
                               f"{page}/{len(news_list)}:\n{news_list[page-1]}",
                               disable_notification=True,
                               reply_markup=navigation_btns)
    except IndexError:
        await bot.send_message(chat_id, "¯\_(ツ)_/¯")


# CURRENCY / EXCHANGE
@dp.callback_query_handler(lambda c: c.data in ['kurs'])
async def currency_command(message: types.Message):
    chat = Chat(message['message']["chat"]["id"])
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    keyboard = types.InlineKeyboardMarkup()

    usd_rates = types.InlineKeyboardButton(text='USD', callback_data='USD')
    eur_rates = types.InlineKeyboardButton(text='EUR', callback_data='EUR')
    rub_rates = types.InlineKeyboardButton(text='RUB', callback_data='RUB')

    exchange_btn = types.InlineKeyboardButton(text=multilang.currency_lang[chat.chat_language]['name'],
                                              callback_data='Exchange')

    keyboard.row(usd_rates, eur_rates, rub_rates)
    keyboard.add(exchange_btn)
    await bot.send_message(message["message"]["chat"]["id"],
                           multilang.currency_lang[chat.chat_language]['choice'],
                           reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['USD', 'EUR', 'RUB'])
async def currency_callback(call: types.CallbackQuery):
    await bot.send_message(call["message"]["chat"]["id"], kurs.get_currency_rates(call['data']))


@dp.callback_query_handler(lambda c: c.data == 'Exchange')
async def exchange_callback(call: types.CallbackQuery):
    chat = Chat(call['message']["chat"]["id"])
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = multilang.currency_lang[chat.chat_language]['help']
    await bot.send_message(call["message"]["chat"]["id"], msg)


# APHORISM
@dp.message_handler(commands=['aphorism'])
async def _users_command(message: types.Message):
    chat = Chat(message["chat"]["id"])
    await bot.delete_message(message["chat"]["id"], message["message_id"])
    aphorism_answer = aphorism.get_aphorism(chat.chat_language)
    await message.answer(aphorism_answer)


@dp.callback_query_handler(lambda c: c.data in ['aphorism'])
async def aphorism_command(message: types.Message):
    chat = Chat(message["message"]["chat"]["id"])
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    aphorism_answer = aphorism.get_aphorism(chat.chat_language)
    await bot.send_message(message["message"]["chat"]["id"], aphorism_answer)


# REMINDERS
@dp.callback_query_handler(lambda c: c.data in ['reminder'])
async def reminder_command(message: types.Message):
    chat = Chat(message["message"]["chat"]["id"])
    msg = rcl['help'][chat.chat_language]

    keyboard = types.InlineKeyboardMarkup()
    saved_reminders_btn = types.InlineKeyboardButton(text=rcl["saved"][chat.chat_language],
                                                     callback_data='show_reminders')

    keyboard.add(saved_reminders_btn)

    await bot.send_message(message["message"]["chat"]["id"], msg, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['show_reminders',
                                                'delete_reminders',
                                                'delete_reminders_confirm_yes',
                                                'delete_reminders_confirm_no'])
async def reminder_callback(call: types.CallbackQuery):
    chat = Chat(call['message']["chat"]["id"])
    if call['data'] == 'show_reminders':
        keyboard = types.InlineKeyboardMarkup()
        delete_reminders_btn = types.InlineKeyboardButton(text=rcl["del_reminders"][chat.chat_language],
                                                          callback_data='delete_reminders')
        keyboard.add(delete_reminders_btn)

        reminders_str = reminder.get_reminders(call['from']['id'])
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        if len(reminders_str) > 0:
            await bot.send_message(call["from"]["id"], reminders_str, reply_markup=keyboard)
        else:
            await bot.send_message(call["from"]["id"], rcl["empty_list"][chat.chat_language])

    if call['data'] == 'delete_reminders':

        keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
        confirm_yes_btn = types.InlineKeyboardButton(text=rcl["yes_delete"][chat.chat_language],
                                                     callback_data='delete_reminders_confirm_yes')
        confirm_no_btn = types.InlineKeyboardButton(text=rcl["not_delete"][chat.chat_language],
                                                    callback_data='delete_reminders_confirm_no')

        keyboard.row(confirm_yes_btn, confirm_no_btn)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call["from"]["id"], rcl["sure"][chat.chat_language], reply_markup=keyboard)

    if call['data'] == 'delete_reminders_confirm_yes':
        reminder.del_reminders(call['from']['id'])
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call["from"]["id"], rcl["deleted"][chat.chat_language])

    if call['data'] == 'delete_reminders_confirm_no':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call["from"]["id"], rcl["decision"][chat.chat_language])


# ORACUL
@dp.callback_query_handler(lambda c: c.data in ['oracul'])
async def with_puree(message: types.Message):
    chat = Chat(message["message"]["chat"]["id"])
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    await bot.send_message(message["message"]["chat"]["id"], oracul.get_prediction(chat.chat_language))


# GET LOCATION
@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    chat = Chat(message["message"]["chat"]["id"])
    tzf = TimezoneFinder()
    user = User(message.from_user.id)
    time_zone = tzf.timezone_at(lng=message.location.longitude, lat=message.location.latitude)
    user.update_timezone(time_zone)
    await bot.delete_message(message["message"]["chat"]["id"], message["message"]["message_id"])
    await message.answer(multilang.keyboards_lang[chat.chat_language]['timezone_updated'])


# LANGUAGE
@dp.message_handler(Text(equals=[multilang.keyboards_lang[k]['lang_change'] for k in multilang.keyboards_lang]))
@dp.message_handler(commands=['language'])
async def _menu_command(message: types.Message):
    chat = Chat(message["chat"]["id"])
    keyboard = types.InlineKeyboardMarkup()
    for lang in multilang.lang_collection.keys():
        keyboard.add(types.InlineKeyboardButton(text=multilang.lang_collection[lang], callback_data=lang))
    await message.answer(multilang.lang_change_option[chat.chat_language], reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['ru_lang', 'ukr_lang'])
async def with_puree(call: types.CallbackQuery):
    chat = Chat(call["message"]["chat"]["id"])
    new_lang = call['data'].split('_')[0]
    chat.chat_language = new_lang
    await call.message.answer(multilang.lang_change[new_lang],
                              reply_markup=keyboards.location_keyboard(call["message"], chat.chat_language))


# COMMON MESSAGE HANDLER
@dp.message_handler()
async def message_handler(message: types.Message):
    answer = short_talk.short_talk_answer(message=message)
    if answer:
        await message.answer(answer)

logging.basicConfig(level=logging.INFO)
