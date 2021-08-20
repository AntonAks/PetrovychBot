import boto3
import json
import settings
from random import choice
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

blacklist_answers = ('Я не хочу с тобой говорить',
                     "Sorry but for some reason you have been trapped in to the black list ┐(°,ʖ°)┌")

s3 = boto3.resource('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_id: int):
        self.access_id = access_id
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if int(message.from_user.id) != int(self.access_id):
            await message.answer("Access Denied")
            raise CancelHandler()


class BlackListMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        short_talks_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, "black_list_users.json")
        body = short_talks_obj.get()['Body'].read().decode("utf-8")
        black_list_users = json.loads(body)['id_set']

        if int(message.from_user.id) in black_list_users:
            await message.answer(choice(blacklist_answers))
            raise CancelHandler()
