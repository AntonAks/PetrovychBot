from aiogram import types
from multilang import keyboards_lang


def main_keyboard(chat_lang):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    oracul_button = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]['oracul'], callback_data='oracul')
    news_button = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]['news'], callback_data='news')
    kurs_button = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]['kurs'], callback_data='kurs')
    aphorism_button = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]['aphorism'], callback_data='aphorism')
    reminder_button = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]['reminder'], callback_data='reminder')

    keyboard.add(news_button)
    keyboard.add(kurs_button)
    keyboard.add(aphorism_button)
    keyboard.add(oracul_button, reminder_button)

    return keyboard


def location_keyboard(msg, chat_lang):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu_button = types.KeyboardButton(keyboards_lang[chat_lang]['menu'])
    language_button = types.KeyboardButton(keyboards_lang[chat_lang]['lang_change'])
    keyboard.add(menu_button)
    keyboard.add(language_button)

    if msg["chat"]["type"] == 'private':
        location_button = types.KeyboardButton(keyboards_lang[chat_lang]['location_update'], request_location=True)
        keyboard.add(location_button)

    return keyboard
