from datetime import datetime, timedelta
import re
from aiogram import Router, F
from aiogram.types import Message

import database
from others.constants import OWN_ID

db = database.Connect(OWN_ID[0])
uidsprof = db.get_profmat_ids()
del db

router = Router()

@router.message(
    (F.text.regexp(f"профмат - .*", flags=re.I) |
    F.text.regexp(fr"профмат \d\d\.\d\d - .*", flags=re.I)),
    F.from_user.id.in_(uidsprof)
)
async def add_homework_simple_format(ms: Message):
    homework = ms.text[ms.text.find('-')+2:].strip()

    if re.fullmatch("профмат - .*", ms.text.lower()):
        today = datetime.today() + timedelta(1)
        date = (today + timedelta((5 - today.weekday() + 7) % 7)).strftime("%d.%m")

    elif re.fullmatch(r"профмат \d\d\.\d\d - .*", ms.text.lower()):
        date = re.findall(r"\d\d\.\d\d", ms.text)[0]
        month = int(date.split('.')[1])
        day = int(date.split('.')[0])
        dat = datetime(datetime.now().year,month, day).isoweekday()
        if dat != 6:
            await ms.answer("Выбранная дата не суббота!")
            return
        
    db = database.Connect(ms.from_user.id)
    db.add_hw_profmat(homework, date)
    await ms.answer(f"Домашнее задание по профмат было добавлено на {date}")

