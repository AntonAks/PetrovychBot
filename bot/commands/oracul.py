import boto3
import settings
import json
from nlp_engine import get_levenshtein_distance
from random import choice

ORACUL_COMMANDS = ['что меня ждет?',
                   'что ждет меня?',
                   'открой будущее',
                   'предскажи будущее',
                   'укажи путь',
                   ]


def is_oracul_command(text) -> bool:
    text = text.lower().replace('петрович', '').strip()
    text = text.lower().replace(',', '').strip()

    for i in ORACUL_COMMANDS:
        get_levenshtein_distance(i, text)

    if any(get_levenshtein_distance(x.lower(), text.lower())[2] for x in ORACUL_COMMANDS):
        return True

    return False


def get_prediction():

    s3 = boto3.resource('s3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                        )

    predictions_list_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, "predictions_list.json")
    body = predictions_list_obj.get()['Body'].read().decode("utf-8")
    predictions_list = json.loads(body)
    predictions = predictions_list['predictions_list']
    answer = choice(predictions)
    return answer
