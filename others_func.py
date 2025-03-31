import calendar
from datetime import date, datetime, timedelta
import json
import logging
from queue import Empty

from aiogram.utils.media_group import MediaGroupBuilder
from constants import LESSONS, SHORTCUTS

days_of_week = {1: 'пн', 2: 'вт', 3: 'ср', 4: 'чт', 5: 'пт', 6: 'сб', 7: "вс"}

WEEKDAYS_DICT = {
    'понедельник': calendar.MONDAY,
    'вторник': calendar.TUESDAY,
    'среда': calendar.WEDNESDAY,
    'четверг': calendar.THURSDAY,
    'пятница': calendar.FRIDAY,
    'суббота': calendar.SATURDAY
}


def get_closest_lesson(lesson: str, class_name: str) -> str:
    with open('schedule.json') as file:
        array = json.loads(file.read())
    array = dict(array[class_name])
    print(array)
    day_interval = 1
    while True:
        date = (datetime.now() + timedelta(day_interval))
        day_week = days_of_week[date.isoweekday()]
        if lesson in array[day_week]:
            print(date.strftime('%d.%m'))
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
    with open('schedule.json') as file:
        lessons = json.loads(file.read())[class_name][weekday]
    return lesson in lessons


def is_admin(uid: int) -> bool:
    with open('schedule.json') as f:
        data = json.load(f)
        for class_ in data.values():
            return uid in class_['admins'] or uid in class_['own']
        
async def get_hw(homework, ms):
    try:
        res = []
        for lesson, hw in homework.items():
            res.append(f'{lesson} - {hw}')
        if res:
            for i in res:
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
                        await ms.answer_media_group(
                            media=album_builder.build()
                        )

                else:
                    for j in array_hw:
                        text += f"\n- {j}"
                    else:
                        await ms.answer(text)
        else:
            await ms.answer('Нет дз')
    except Exception as e:
                logging.error(f'Ошибка get_hw_other: {e}')