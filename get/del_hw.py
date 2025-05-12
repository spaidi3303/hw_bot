from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder

import database
from others.constants import ENGLISH_LESSONS, RUSSIAN_LESSONS

router = Router()


@router.callback_query(F.data.startswith("deldz"))
async def call(query: CallbackQuery):
    date = query.data.split(':')[1]
    lesson = ENGLISH_LESSONS[query.data.split(':')[2]]
    text = query.message.text
    spl = text.split("\n")
    text = text.replace(spl[0], f"Какое дз вы хотите удалить по {lesson}?")
    for i, sp in enumerate(spl, 1):
        if sp.startswith('-'):
            text = sp, f'{i}) {sp}'
    await query.message.edit_text(text,
                                  reply_markup=del_hw_builder(len(spl), date, RUSSIAN_LESSONS[lesson]))


class DelHwClass(CallbackData, prefix="hwdel"):
    lesson: str
    date: str
    index: str


def del_hw_builder(count, date, lesson):
    builder = InlineKeyboardBuilder()
    for i in range(1, count):
        builder.button(text=f"{i}", callback_data=DelHwClass(lesson=lesson, date=date, index=f"{i}"))
    return builder.as_markup()


@router.callback_query(DelHwClass.filter())
async def call(query: CallbackQuery, callback_data: DelHwClass):
    lesson = ENGLISH_LESSONS[callback_data.lesson]
    date = callback_data.date
    index = callback_data.index
    db = database.Connect(query.from_user.id)
    db.del_hw(date, lesson, int(index))
    await query.message.edit_text("Домашняя работа была удалена")
