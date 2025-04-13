import calendar
from datetime import date, datetime, timedelta
import json
import logging
from queue import Empty
import re
from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder
from others.constants import LESSONS, OWN_CLASS, OWN_ID, SHORTCUTS
import database

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
        print(day_week)
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


def is_admin(uid: int) -> bool:
    db = database.Connect(uid)
    res = db.get_admins()
    return (uid == res['own']) or (uid in res['admins'])


async def get_hw(homework, uid: int,  ms: Message | None = None, bot: Bot | None = None):
    try:
        res = []
        for lesson, hw in homework.items():
            res.append(f'{lesson} - {hw}')
        if res:
            for i in res:
                if re.findall(r"\d\d\.\d\d", i):
                    idate = i.split("-")[0].strip()
                    today = datetime.now()
                    current_year = today.year
                    date = datetime.strptime(f"{current_year}-{idate.split(".")[1]}-{idate.split(".")[0]}", "%Y-%m-%d")
                    if date < today:
                        continue
                
                text = f"{i[:i.index("-")-1]}:"
                hw = i[i.index("-")+2:]
                array_hw = json.loads(hw.replace("'", '"'))
                if any(isinstance(item, list) for item in array_hw):
                    photo_ids = []
                    for j in array_hw:
                        if isinstance(j, str):
                            text += f"\n- {j}"
                        elif isinstance(j, list):
                            for file_id in j:
                                photo_ids.append(file_id)
                    if photo_ids is not Empty:
                        album_builder = MediaGroupBuilder(
                            caption=text
                        )
                        for fi_id in photo_ids:
                            album_builder.add_photo(
                                media=fi_id
                            )
                        if ms is not None:
                            await ms.answer_media_group(
                                media=album_builder.build()
                            )
                        else:
                            await bot.send_media_group(
                                chat_id=uid,
                                media=album_builder.build()
                            )

                else:
                    for j in array_hw:
                        text += f"\n- {j}"
                    else:
                        if ms is not None:
                            await ms.answer(text)
                        else:
                            await bot.send_message(uid, text)
        else:
            if ms is not None:
                await ms.answer('Нет дз')
            else:
                await bot.send_message(uid, 'Нет дз')
            
    except Exception as e:
        logging.error(f'Ошибка get_hw_other: {e}')