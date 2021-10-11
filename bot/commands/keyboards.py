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


def beer_choice_abv(chat_lang):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    non_alcohol_btn = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]["beer_abv_na"], callback_data=f"No Alco")
    low_alcohol_btn = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]["beer_abv_low"], callback_data=f"Low")
    mid_alcohol_btn = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]["beer_abv_mid"], callback_data=f"Mid")
    high_alcohol_btn = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]["beer_abv_high"], callback_data=f"High")

    keyboard.add(non_alcohol_btn)
    keyboard.add(low_alcohol_btn)
    keyboard.add(mid_alcohol_btn)
    keyboard.add(high_alcohol_btn)
    return keyboard


def beer_choice_ibu(abv_choice, chat_lang):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    low_ibu_btn = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]["beer_ibu_low"], callback_data=f"{abv_choice}-Low")
    mid_ibu_btn = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]["beer_ibu_mid"], callback_data=f"{abv_choice}-Mid")
    high_ibu_btn = types.InlineKeyboardButton(text=keyboards_lang[chat_lang]["beer_ibu_high"], callback_data=f"{abv_choice}-High")

    keyboard.add(low_ibu_btn)
    keyboard.add(mid_ibu_btn)
    keyboard.add(high_ibu_btn)
    return keyboard

