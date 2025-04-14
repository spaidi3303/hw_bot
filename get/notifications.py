from datetime import datetime, timedelta

from aiogram import Bot

from database import Connect
from others.others_func import get_hw


async def send_homework(bot: Bot):
    db = Connect(0)
    all_ids = db.get_all_id()
    profid = db.get_profmat_ids()
    del db
    for uid in all_ids:
        db = Connect(uid)
        class_name = db.get_class_id(uid)
        tomorrow = datetime.now() + timedelta(days=1)
        homeworks = db.get_all_homework(class_name, tomorrow.strftime('%d.%m'))
        await get_hw(homeworks, uid, bot=bot)

        if uid in profid:
            if tomorrow.isoweekday() == 6:
                hw = db.get_hw_profmat()
                text = "Профильная математика: \n"
                try: 
                    for hw_i in hw[tomorrow.strftime('%d.%m')]:
                        text += f"- {hw_i}\n\n"
                except:
                    return
                await bot.send_message(text)
                