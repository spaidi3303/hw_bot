from datetime import datetime, timedelta
import json
from queue import Empty
import re

from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder
from constants import WEEKDAYS
import database
from others_func import get_hw, get_prope_date

router = Router()


@router.message(
    (F.text.lower() == 'дз') |
    F.text.lower().regexp(r'^дз \d\d\.\d\d$') |
    F.text.lower().regexp(fr'^дз ({'|'.join(WEEKDAYS)})$')
)
async def get_homework(ms: Message):
    db = database.Connect(ms.from_user.id)
    class_name = db.get_class()
    text = ms.text.lower()
    if text == 'дз':
        tomorrow = datetime.now() + timedelta(days=1)
        homeworks = db.get_all_homework(class_name, tomorrow.strftime('%d.%m'))
    elif re.fullmatch(r'^дз \d\d\.\d\d$', text):
        date = ms.text.split()[-1]
        homeworks = db.get_all_homework(class_name, date)
    elif re.fullmatch(fr'^дз ({'|'.join(WEEKDAYS)})$', text):
        weekday = ms.text.split()[-1]
        date = get_prope_date(weekday)
        homeworks = db.get_all_homework(class_name, date)

    await get_hw(homeworks, ms)
    
