import json
import boto3
import settings
from random import choice
from nlp_engine import find_answer
from commands.kurs import exchange_currency
from commands.oracul import is_oracul_command, get_prediction
from commands.reminder import create_reminder


s3 = boto3.resource('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )

short_talks_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, "short_talks.json")
body = short_talks_obj.get()['Body'].read().decode("utf-8")
short_talks = json.loads(body)


def short_talk_answer(message) -> str:
    text = message['text']

    if text.lower().startswith('обмен') or text.lower().startswith('меняю'):
        answer = exchange_currency(text)
        return answer

    if text.replace(',', '').split()[0].lower() in ['напомни', 'напомнить', 'напомнишь']:
        answer = create_reminder(message)
        return answer

    if is_oracul_command(text):
        answer = get_prediction()
        return answer

    answer_key = find_answer(text, short_talks)
    answer = choice(short_talks[answer_key]['answer'])
    return answer
