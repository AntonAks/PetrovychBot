import boto3
import settings
import json
from nltk_engine import model


s3 = boto3.resource('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )

short_talks_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, "short_talks.json")
body = short_talks_obj.get()['Body'].read().decode("utf-8")
short_talks = json.loads(body)


if __name__ == '__main__':
    model.train(short_talks)


