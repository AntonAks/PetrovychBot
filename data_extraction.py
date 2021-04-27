import boto3
import settings
import json
import os
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from db import messages_collection


def upload_to_s3(local_file):

    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                             )

    _date_time = datetime.now().strftime('%Y%m%d_%H%M%S')

    try:
        s3_client.upload_file(local_file, settings.AWS_S3_BUCKET_NAME, f'chat_info/{_date_time}_chat.json')
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def get_chat_data():

    mongo_cursor = messages_collection.find()
    messages = list(mongo_cursor)
    messages_converted = []
    for m in messages:
        messages_converted.append({'_id': str(m['_id']), 'correct': m['correct'], 'message': m['message']})

    with open("temp.json", "w", encoding="utf-8") as outfile:
        json.dump(messages_converted, outfile, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    get_chat_data()
    upload_to_s3("temp.json")
    os.remove("temp.json")
