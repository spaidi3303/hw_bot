import asyncio
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from others.constants import LESSONS, SHORTCUTS, WEEKDAYS
import database
from others.others_func import get_closest_lesson, get_lesson_full_name, get_prope_date, is_admin, is_lesson_in_date

router = Router()


class PhotoAlbumState(StatesGroup):
    waiting_for_album = State()  # Состояние для сбора альбома


@router.message(F.photo)
async def handle_photo_album(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Ты не админ!")
        return
    current_data = await state.get_data()
    if "photos" not in current_data:
        await state.update_data(photos=[], caption=None)
        current_data = await state.get_data()
    photo_id = message.photo[-1].file_id
    if photo_id not in [p["file_id"] for p in current_data.get("photos", [])]:
        updated_photos = current_data["photos"] + [{"file_id": photo_id, "caption": message.caption}]
        await state.update_data(photos=updated_photos)
    if message.caption:
        await state.update_data(caption=message.caption)
    await asyncio.sleep(2)
    current_data = await state.get_data()
    if "photos" in current_data:
        photos = current_data["photos"]
        caption = current_data.get("caption")
        photoid_array = [p['file_id'] for p in photos]
        await state.clear()
        await add_homework_photos(caption, photoid_array, message)


async def add_homework_photos(caption: str, photos: list, message: Message):
    print(photos)
    db = database.Connect(message.from_user.id)
    lesson = ""
    date = ""
    class_name = db.get_class()

    if re.fullmatch(f"^({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())})$", caption.lower()):
        lesson = get_lesson_full_name(caption)
        date = get_closest_lesson(lesson, class_name)
    elif re.fullmatch(fr"^({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())}) \d\d\.\d\d$", caption.lower()):
        date = re.findall(r"\d\d\.\d\d", caption)[0]
        index = (caption.index(re.findall(r"\d", caption)[0]))
        lesson = get_lesson_full_name(str(caption[:index]))
    elif re.fullmatch(fr"^({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())}) ({'|'.join(WEEKDAYS)})$", caption.lower()):
        weekday = re.findall(f"{'|'.join(WEEKDAYS)}", caption)[0]
        date = get_prope_date(weekday)
        lesson = caption[:caption.find(weekday)]
        lesson = get_lesson_full_name(lesson)
    else:
        return
    if not is_lesson_in_date(lesson, date, class_name):
            await message.answer(f"Урок {lesson} в указанный день не найден.")
            return   
    db.update_homework(class_name, lesson, date, photos)
    await message.answer(f"Домашнее задание было добавлено в {lesson} на {date}")