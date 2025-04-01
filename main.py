import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.methods import DeleteWebhook
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from notifications import send_homework
import routers

load_dotenv("secret.env") 
TOKEN = os.getenv("token")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
dp.include_router(routers.router)

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
    await bot(DeleteWebhook(drop_pending_updates=True))
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    dp.startup.register(on_startup)
    asyncio.run(main())
