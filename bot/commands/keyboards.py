from aiogram import types


def main_keyboard(msg):
    print(msg["chat"]["type"])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    oracul_button = types.KeyboardButton("Что меня ждёт?")
    news_button = types.KeyboardButton("Новости")
    kurs_button = types.KeyboardButton("Курс валют")
    aphorism_button = types.KeyboardButton('Афоризм')
    reminder_button = types.KeyboardButton('Напоминания')

    keyboard.add(news_button)
    keyboard.add(kurs_button)
    keyboard.add(aphorism_button)
    keyboard.add(oracul_button, reminder_button)

    if msg["chat"]["type"] == 'private':
        reg_button = types.KeyboardButton("Обновить часовой пояс", request_location=True)
        keyboard.add(reg_button)

    return keyboard
