from db import reminder_collection
import re

import datetime


def save_reminder_to_db(chat_id, from_id, from_username, create_date, remind_at, msg):

    reminder_collection.insert_one({
        "Date": datetime.datetime.now(),
        "Reminder": {
            "chat_id": chat_id,
            "from_id": from_id,
            "from_username": from_username,
            "create_date": create_date,
            "remind_at": remind_at,
            "text": msg,
        },
        "Active": True
    })

    return "Будет сделано!"


def create_reminder(message):

    text = message['text']
    chat_id = message['chat']['id']
    from_id = message['from']['id']
    from_username = message['from']['username']
    create_date = message['date']

    split_text = text.replace(',', '').split()

    try:
        reminder_time = re.search(r'([0-9]|[0-9]\d|2[0-3]):([0-5]\d)', text).group()
        reminder_text = text[text.index(reminder_time):].replace(reminder_time, '').strip()
    except AttributeError:
        return "Формат времени или значение времени введено не коректно.", False

    try:
        reminder_date = re.search(r'([0-9]\d)\.([0-9]\d)\.([0-9]*)', text).group()
    except AttributeError:
        reminder_date = None

    date = datetime.datetime.today()

    if split_text[2] in ['завтра']:
        date = date + datetime.timedelta(days=1)

    if reminder_date:
        try:
            reminder_date = reminder_date.split('.')
            date = datetime.datetime(year=int(reminder_date[2]),
                                     month=int(reminder_date[1]),
                                     day=int(reminder_date[0]))
        except ValueError:
            return "Формат даты или значения даты введены не коректно.", False

    try:
        remind_at = datetime.datetime(year=date.year,
                                      month=date.month,
                                      day=date.day,
                                      hour=int(reminder_time.split(':')[0]),
                                      minute=int(reminder_time.split(':')[1]))
    except ValueError:
        return "Формат времени или значение времени введено не коректно.", False

    if remind_at < datetime.datetime.now():
        return "Боюсь что это это время уже настало или прошло...", False

    answer = save_reminder_to_db(chat_id, from_id, from_username, create_date, remind_at, reminder_text)

    return answer, True


def check_reminder():
    mongo_cursor = reminder_collection.find({"Active": True}, {"Reminder", "Active"})
    alerts = list(mongo_cursor)
    now = datetime.datetime.now()

    send_list = []

    for i in alerts:
        if i['Reminder']['remind_at'] < now:
            reminder_collection.update_one({"_id": i["_id"]}, {"$set": {"Active": False}})
            send_list.append({'user': i['Reminder']['from_id'], 'text': i['Reminder']['text']})

    return send_list


if __name__ == '__main__':
    pass
