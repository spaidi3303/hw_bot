from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder, InlineKeyboardButton

from others.constants import ENGLISH_LESSONS

router = Router()

@router.callback_query(F.data.startswith("deldz"))
async def call(query: CallbackQuery):
    date = query.data.split(':')[1]
    lesson = ENGLISH_LESSONS[query.data.split(':')[2]]
    print(date, lesson)
