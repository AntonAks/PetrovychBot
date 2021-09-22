from aiogram import types


def main_keyboard():
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    oracul_button = types.InlineKeyboardButton(text='Что меня ждёт?', callback_data='oracul')
    news_button = types.InlineKeyboardButton(text='Новости', callback_data='news')
    kurs_button = types.InlineKeyboardButton(text='Курс валют', callback_data='kurs')
    aphorism_button = types.InlineKeyboardButton(text='Афоризм', callback_data='aphorism')
    reminder_button = types.InlineKeyboardButton(text='Напоминания', callback_data='reminder')

    keyboard.add(news_button)
    keyboard.add(kurs_button)
    keyboard.add(aphorism_button)
    keyboard.add(oracul_button, reminder_button)

    return keyboard


def location_keyboard(msg):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu_button = types.KeyboardButton("Меню")
    keyboard.add(menu_button)

    if msg["chat"]["type"] == 'private':
        location_button = types.KeyboardButton("Обновить часовой пояс", request_location=True)
        keyboard.add(location_button)

    return keyboard
