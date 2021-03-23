from aiogram import executor

from logic import bot, dp

try:
    import local_settings as settings
except ImportError:
    import _local_settings as settings


ACCESS_ID = settings.ACCESS_ID


async def on_shutdown(dp):
    await bot.send_message(ACCESS_ID, "By!")
    await bot.close()


async def on_startup(dp):
    await bot.send_message(ACCESS_ID, "I'm here")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
