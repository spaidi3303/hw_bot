import calendar
import logging
from datetime import date, datetime, timedelta
import json
import re

from aiogram import Bot
from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database
from others.constants import LESSONS, OWN_CLASS, SHORTCUTS, RUSSIAN_LESSONS

days_of_week = {1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday', 6: 'saturday', 7: 'sunday'}

WEEKDAYS_DICT = {
    'понедельник': calendar.MONDAY,
    'вторник': calendar.TUESDAY,
    'среда': calendar.WEDNESDAY,
    'четверг': calendar.THURSDAY,
    'пятница': calendar.FRIDAY,
    'суббота': calendar.SATURDAY
}


def get_closest_lesson(lesson: str, class_name: str) -> str:
    db = database.Connect(OWN_CLASS[class_name])
    array = db.get_lessons()
    day_interval = 1
    while True:
        date = (datetime.now() + timedelta(day_interval))
        day_week = days_of_week[date.isoweekday()]
        if lesson in array[day_week]:
            return date.strftime('%d.%m')
        day_interval = day_interval + 1


def get_prope_date(weekday: str) -> str:
    today = date.today()
    offset = (WEEKDAYS_DICT[weekday] - today.weekday()) % 7
    return (today + timedelta(days=offset)).strftime('%d.%m')


def get_lesson_full_name(lesson: str) -> str | None:
    lesson = lesson.lower().strip()
    if lesson not in LESSONS.keys():
        try:
            return SHORTCUTS[lesson]
        except KeyError:
            return
    else:
        return LESSONS[lesson]


def is_lesson_in_date(lesson: str, date: str, class_name: str) -> bool:
    dates = list(map(int, date.split('.')))
    weekday = days_of_week[datetime(year=datetime.now().year, month=dates[1], day=dates[0]).isoweekday()]
    db = database.Connect(OWN_CLASS[class_name])
    lessons = db.get_lessons()[weekday]
    return lesson in lessons


class is_admin(Filter):
    async def __call__(self, message: Message):
        uid = message.from_user.id
        db = database.Connect(uid)
        res = db.get_admins()
        return (uid == res['own']) or (uid in res['admins'])


async def get_hw(date_hw, lesson_hw, homework, uid: int, ms: Message | None = None, bot: Bot | None = None):
    res = []
    for lesson, hw in homework.items():
        res.append(f'{lesson} - {hw}')
    for i in res:
        if re.findall(r"\d\d\.\d\d", i):
            idate = i.split("-")[0].strip()
            today = datetime.now()
            current_year = today.year
            date_check = datetime.strptime(f"{current_year}-{idate.split(".")[1]}-{idate.split(".")[0]}", "%Y-%m-%d")
            if date_check < today:
                return
        text = f"{i[:i.index("-")-1]}:"
        hw = i[i.index("-")+2:]
        hw = hw.replace('"', "*")
        array_hw = json.loads(hw.replace("'", '"'))

        if any(isinstance(item, list) for item in array_hw):
            photo_ids = []
            for j in array_hw:
                if isinstance(j, str):
                    text += f"\n- {j}"
                elif isinstance(j, list):
                    for file_id in j:
                        photo_ids.append(file_id)
            if photo_ids:
                album_builder = MediaGroupBuilder(caption=text)
                for fi_id in photo_ids:
                    album_builder.add_photo(media=fi_id)
                await _send_media_group(album_builder.build(), uid, ms, bot)
        else:
            db = database.Connect(uid)
            admins = db.get_admins()
            isAdmin = uid in admins['admins'] or uid == admins['own']
            del db
            for j in array_hw:
                text += f"\n- {j}"
            else:
                if isAdmin:
                    await _send_ms(text, uid, ms, bot, reply_markup=DelHw(date_hw, lesson_hw))
                else:
                    await _send_ms(text, uid, ms, bot)

def DelHw(date_hw, lesson):
    builder = InlineKeyboardBuilder()
    builder.button(text="Удалить дз", callback_data=f"deldz:{date_hw}:{RUSSIAN_LESSONS[lesson]}")
    return builder.as_markup()


async def _send_ms(text: str, uid: int, ms: Message | None, bot: Bot | None, **kwargs):
    if ms is not None:
        await ms.answer(text, **kwargs)
    else:
        await bot.send_message(uid, text, **kwargs)


async def _send_media_group(media, uid: int, ms: Message | None, bot: Bot | None):
    if ms is not None:
        await ms.answer_media_group(media=media)
    else:
        await bot.send_media_group(chat_id=uid, media=media)
