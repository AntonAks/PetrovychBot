import json
import boto3
import settings
from random import choice
from engine import get_levenshtein_distance
from bot_commands.kurs import exchange_currency


s3 = boto3.resource('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )

obj = s3.Object(settings.AWS_S3_BUCKET_NAME, "short_talks.json")
body = obj.get()['Body'].read().decode("utf-8")
short_talks = json.loads(body)


def short_talk_answer(message) -> tuple:
    keys = short_talks.keys()
    for key in keys:
        for phrase in short_talks[key]['phrase']:
            if get_levenshtein_distance(phrase, message)[2] or \
                    get_levenshtein_distance('Петрович ' + phrase, message)[2] or \
                    get_levenshtein_distance(phrase + ' Петрович', message)[2]:
                answer = choice(short_talks[key]['answer']), True
                return answer

    if message.lower().startswith('обмен') or message.lower().startswith('меняю'):
        answer = exchange_currency(message)
        return answer

    if 'петрович' in message.lower():
        answer = choice(short_talks['Unknown']['answer']), False
        return answer
