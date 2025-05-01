from datetime import datetime, timedelta
import re
from others.constants import LESSONS, SHORTCUTS
import database
from others.others_func import get_hw, get_lesson_full_name
from aiogram import Router, F
from aiogram.types import Message
from others.constants import WEEKDAYS
from others.others_func import get_prope_date

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
    date = ""
    if text == 'дз':
        date = (datetime.now() + timedelta(days=1)).strftime('%d.%m')
    elif re.fullmatch(r'^дз \d\d\.\d\d$', text):
        date = ms.text.split()[-1]
    elif re.fullmatch(fr'^дз ({'|'.join(WEEKDAYS)})$', text):
        weekday = ms.text.split()[-1]
        date = get_prope_date(weekday)
    homeworks = db.get_all_homework(class_name, date)
    print(homeworks)
    await get_hw(homeworks, ms.from_user.id, ms=ms)


@router.message(F.text.lower().regexp(f'^дз ({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())})$'))
async def get_homework_keyboard(ms: Message):
    lesson = ms.text[3:]
    lesson = get_lesson_full_name(lesson)
    db = database.Connect(ms.from_user.id)
    all_dates = db.get_all_dates(lesson)
    if all_dates.__len__() == 0:
        await ms.answer("По этому предмету нет дз")
        return
    homework = db.get_homework(db.get_class(), get_lesson_full_name(lesson))
        
    await get_hw(homework, ms.from_user.id, ms=ms)


@router.message(F.text.lower() == "дз профмат")
async def get_profmat_hw(ms: Message):
    db = database.Connect(ms.from_user.id)
    homework = db.get_hw_profmat()
    await get_hw(homework, ms.from_user.id, ms=ms)
