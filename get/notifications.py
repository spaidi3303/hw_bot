from datetime import datetime, timedelta

from aiogram import Bot

from database import Connect
from others.others_func import get_hw


async def send_homework(bot: Bot):
    db = Connect(0)
    all_ids = db.get_all_id()
    for uid in all_ids:
        class_name = db.get_class_id(uid)
        tomorrow = datetime.now() + timedelta(days=1)
        homeworks = db.get_all_homework(class_name, tomorrow.strftime('%d.%m'))
        await get_hw(homeworks, bot=bot, uid=uid)
