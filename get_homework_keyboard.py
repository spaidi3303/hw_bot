import json
from queue import Empty

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder, InlineKeyboardButton

from constants import LESSONS, SHORTCUTS
import database
from others_func import get_hw, get_lesson_full_name

router = Router()


class ActionListDates(CallbackData, prefix="date"):
    class_name: str
    lesson: str
    date: str


@router.message(F.text.lower().regexp(f'^дз ({'|'.join(LESSONS.keys())}|{'|'.join(SHORTCUTS.keys())})$'))
async def get_homework_keyboard(ms: Message):
    lesson = ms.text[3:]
    lesson = get_lesson_full_name(lesson)

    db = database.Connect(ms.from_user.id)

    await ms.answer('Выбери дату, на которую тебе нужна домашка:',
                    reply_markup=await dates_buttons(db.get_all_dates(lesson), db.get_class(), lesson))


@router.callback_query(ActionListDates.filter())
async def on_date_choice(query: CallbackQuery, callback_data: ActionListDates):
    db = database.Connect(query.message.from_user.id)
    homework = db.get_homework(callback_data.class_name, get_lesson_full_name(callback_data.lesson))
    res = []
    for lesson, hw in homework.items():
        res.append(f'{lesson} - {hw}')
        
    await get_hw(homework, query.message)


async def dates_buttons(dates: list[str], class_name: str, lesson: str):
    builder = InlineKeyboardBuilder()
    for date in dates:
        builder.row(InlineKeyboardButton(text=date,
                                         callback_data=ActionListDates(class_name=class_name,
                                                                       lesson=lesson,
                                                                       date=date
                                                                      ).pack()
                                        )
                   )
    builder.adjust(3)
    return builder.as_markup()
