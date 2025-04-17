import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from get.notifications import send_homework
from others.constants import OWN_ID
import others.routers as routers
import error
load_dotenv("secret.env") 
TOKEN = os.getenv("token")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
dp.include_routers(routers.router, error.router)


async def send_homework_bot():
    await send_homework(bot)


async def on_startup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_homework_bot,
        'cron',
        hour=16,
        minute=00,
        timezone="Europe/Moscow"
    )
    scheduler.start()


async def main():
    await bot.send_message(OWN_ID[0], "бот запущен")
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
    await bot.send_message(OWN_ID[0], "бот выключен")
if __name__ == "__main__":
    dp.startup.register(on_startup)
    asyncio.run(main())
