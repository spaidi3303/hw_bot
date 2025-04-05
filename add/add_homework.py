import re

from aiogram import Router, F
from aiogram.types import Message

from others.constants import LESSONS, SHORTCUTS, WEEKDAYS
from others.others_func import get_closest_lesson, get_lesson_full_name, get_prope_date, is_admin, is_lesson_in_date
import database

router = Router()


@router.message(
    F.text.regexp(f"({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())}) - .*", flags=re.I) |
    F.text.regexp(fr"({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())}) \d\d\.\d\d - .*", flags=re.I) |
    F.text.regexp(fr"({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())}) ({'|'.join(WEEKDAYS)}) - .*", flags=re.I)
)
async def add_homework_simple_format(message: Message):
    lesson = message.text[: message.text.find('-')].strip()
    homework = message.text[message.text.find('-')+2:].strip()
    db = database.Connect(message.from_user.id)
    if not is_admin(message.from_user.id):
        await message.answer("Ты не админ!")
        return
    class_name = db.get_class()
    text =  message.text.lower().replace('\n', ' ')
    
    if re.fullmatch(f"({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())}) - .*", text):
        lesson = get_lesson_full_name(lesson)
        date = get_closest_lesson(lesson, class_name)

    elif re.fullmatch(fr"({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())}) \d\d\.\d\d - .*", text):
        date = re.findall(r"\d\d\.\d\d", lesson)[0]
        index = (lesson.index(re.findall(r"\d", lesson)[0]))
        lesson = get_lesson_full_name(str(lesson[:index]))
        
    elif re.fullmatch(fr"({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())}) ({'|'.join(WEEKDAYS)}) - .*", text):
        weekday = re.findall(f"{'|'.join(WEEKDAYS)}", message.text)[0]
        date = get_prope_date(weekday)
        lesson = lesson[:lesson.find(weekday)]
        lesson = get_lesson_full_name(lesson)

    try:
        if not is_lesson_in_date(lesson, date, class_name):
            await message.answer(f"Урок {lesson} в указанный день не найден.")
            return
    except ValueError:
        await message.answer('Неправильная дата: ' + date)

    db.update_homework(class_name, lesson, date, homework)
    await message.answer(f"Домашнее задание было добавлено в {lesson} на {date}")
