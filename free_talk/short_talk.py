import json
import boto3
import settings
from random import choice
from engine import get_levenshtein_distance
from bot_commands.kurs import exchange_currency
from bot_commands.reminder import create_reminder
from bot_commands.oracul import is_oracul_command, get_prediction


s3 = boto3.resource('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )

short_talks_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, "short_talks.json")
body = short_talks_obj.get()['Body'].read().decode("utf-8")
short_talks = json.loads(body)


def short_talk_answer(message) -> tuple:

    text = message['text']

    keys = short_talks.keys()
    for key in keys:
        for phrase in short_talks[key]['phrase']:
            if get_levenshtein_distance(phrase, text)[2] or \
                    get_levenshtein_distance('Петрович ' + phrase, text)[2] or \
                    get_levenshtein_distance(phrase + ' Петрович', text)[2]:
                answer = choice(short_talks[key]['answer']), True
                return answer

    if text.lower().startswith('обмен') or text.lower().startswith('меняю'):
        answer = exchange_currency(text)
        return answer

    if 'петрович' in text.lower() and text.replace(',', '').split()[1] in ['напомни', 'напомнить', 'напомнишь']:
        answer = create_reminder(message)
        return answer

    if is_oracul_command(text):
        answer = get_prediction(), True
        return answer

    if 'петрович' in text.lower():
        answer = choice(short_talks['Unknown']['answer']), False
        return answer
