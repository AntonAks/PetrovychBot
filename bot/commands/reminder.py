import logging
import pytz
from db import reminder_collection, User, Chat
import re
import datetime
from multilang import reminder_commands_lang as rcl


def save_reminder_to_db(chat_id, from_id, from_username, create_date, remind_at, msg, user_timezone, language):

    reminder_collection.insert_one({
        "Date": datetime.datetime.now(),
        "Reminder": {
            "chat_id": chat_id,
            "from_id": from_id,
            "from_username": from_username,
            "create_date": create_date,
            "remind_at": remind_at,
            "text": msg,
            "chat_lang": language,
            "user_timezone": str(user_timezone)
        },
        "Active": True
    })

    return rcl['will_be_done'][language]


def create_reminder(message):

    user = User(message['from']['id'])
    chat = Chat(message['chat']['id'])

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
        return rcl['wrong_time_format'][chat.chat_language]

    try:
        reminder_date = re.search(r'([0-9]\d)\.([0-9]\d)\.([0-9]*)', text).group()
    except AttributeError:
        reminder_date = None

    date = datetime.datetime.now(pytz.timezone(user.last_timezone)).replace(tzinfo=None)

    if 'завтра' in split_text:
        date = date + datetime.timedelta(days=1)

    if reminder_date:
        try:
            reminder_date = reminder_date.split('.')
            date = datetime.datetime(year=int(reminder_date[2]),
                                     month=int(reminder_date[1]),
                                     day=int(reminder_date[0]))
        except ValueError:
            return rcl['wrong_time_format'][chat.chat_language]

    try:
        remind_at = datetime.datetime(year=date.year,
                                      month=date.month,
                                      day=date.day,
                                      hour=int(reminder_time.split(':')[0]),
                                      minute=int(reminder_time.split(':')[1]))
    except ValueError:
        return rcl['wrong_time_format'][chat.chat_language]

    if remind_at < datetime.datetime.now(pytz.timezone(user.last_timezone)).replace(tzinfo=None):
        return rcl['time_in_past'][chat.chat_language]

    answer = save_reminder_to_db(chat_id,
                                 from_id,
                                 from_username,
                                 create_date,
                                 remind_at,
                                 reminder_text,
                                 user.last_timezone,
                                 chat.chat_language)

    return answer


def check_reminder():
    mongo_cursor = reminder_collection.find({"Active": True}, {"Reminder", "Active"})
    alerts = list(mongo_cursor)

    send_list = []

    for i in alerts:
        now = datetime.datetime.now(pytz.timezone(i['Reminder']['user_timezone'])).replace(tzinfo=None)
        if i['Reminder']['remind_at'] < now:
            reminder_collection.update_one({"_id": i["_id"]}, {"$set": {"Active": False}})
            send_list.append({'user': i['Reminder']['from_id'],
                              'text': i['Reminder']['text'],
                              'chat_lang': i['Reminder']['chat_lang']})

    return send_list


def get_reminders(_id):
    mongo_cursor = reminder_collection.find({"Active": True, "Reminder.from_id": _id}).sort("Reminder.remind_at", 1)
    reminders = list(mongo_cursor)
    string = ''
    for i in reminders:
        string = string + i['Reminder']['text'] + ' - ' + i['Reminder']['remind_at'].strftime("%Y.%m.%d  %H:%M") + '\n'

    return string


def del_reminders(_id):
    reminder_collection.delete_many({"Active": True, "Reminder.from_id": _id})
    return True
