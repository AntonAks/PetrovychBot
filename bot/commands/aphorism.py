import json
import boto3
import settings
from random import choice


def get_aphorism(language):

    s3 = boto3.resource('s3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                        )

    predictions_list_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, f"{language}/aphorisms.json")
    body = predictions_list_obj.get()['Body'].read().decode("utf-8")
    aphorism = choice(json.loads(body))
    answer_string = aphorism["quoteText"] + '\n'
    answer_string = answer_string + '\n' + f"{aphorism['quoteAuthor']}"

    return answer_string
