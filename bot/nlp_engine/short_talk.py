import json
import boto3
import settings
from db import Chat
from random import choice
from nlp_engine import find_answer
from commands.kurs import exchange_currency
from commands.oracul import is_oracul_command, get_prediction
from commands.reminder import create_reminder
from multilang import short_talks_lang as stl


s3 = boto3.resource('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )


def private_answer(message, language, short_talks) -> str:
    text = message['text']

    if text.lower().startswith(stl['exchange'][language][0]) or text.lower().startswith(stl['exchange'][language][1]):
        answer = exchange_currency(text, language)
        return answer

    if any(word in text.lower() for word in stl['reminder_words'][language]):
        answer = create_reminder(message)
        return answer

    if is_oracul_command(text, language):
        answer = get_prediction(language)
        return answer

    answer_key = find_answer(text, short_talks)
    answer = choice(short_talks[answer_key]['answer'])
    return answer


def group_answer(message, language, short_talks) -> str:
    text = message['text']
    if text.lower().startswith(stl['exchange'][language][0]) or text.lower().startswith(stl['exchange'][language][1]):
        answer = exchange_currency(text, language)
        return answer

    elif 'петрович' in text.lower() and any(word in text.lower() for word in stl['reminder_words'][language]):
        answer = create_reminder(message)
        return answer

    elif is_oracul_command(text, language):
        answer = get_prediction(language)
        return answer

    elif 'петрович' in text.lower():
        text = text.lower()
        text = text.replace('петрович', '')
        answer_key = find_answer(text, short_talks)
        answer = choice(short_talks[answer_key]['answer'])
        return answer

    else:
        return ''


def short_talk_answer(message=None, ) -> str:
    chat = Chat(message["chat"]["id"])
    chat_lang = chat.chat_language

    short_talks_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, f"{chat_lang}/short_talks.json")
    body = short_talks_obj.get()['Body'].read().decode("utf-8")
    short_talks = json.loads(body)

    if message["chat"]["type"] == 'private':
        answer = private_answer(message, chat_lang, short_talks)
    else:
        answer = group_answer(message, chat_lang, short_talks)
    return answer
