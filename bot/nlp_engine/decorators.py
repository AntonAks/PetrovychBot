import boto3
import json
import settings
from random import choice

# TODO: Need to change blacklist_check decorator due to existing handling black list by Middleware

s3 = boto3.resource('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )

blacklist_answers = ('Я не хочу с тобой говорить', 'Мне это не интересно', 'Мне это безразлично')


def blacklist_check(func):
    short_talks_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, "black_list_users.json")
    body = short_talks_obj.get()['Body'].read().decode("utf-8")
    black_list_users = json.loads(body)['id_set']

    def wrapper(*args, **kwargs):
        if kwargs['message']['from']['id'] in black_list_users:
            try:
                name = kwargs['message']['from']['first_name']
            except KeyError:
                name = ''
            answer = f'{choice(blacklist_answers)} {name}'
        else:
            answer = func(*args, **kwargs)
        return answer
    return wrapper


