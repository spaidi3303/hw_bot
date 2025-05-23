from aiogram import Router, F
from aiogram.types import Message

import database


router = Router()

@router.message(F.text.lower() == "расписание")
async def lessons_get(ms: Message):
    uid = ms.from_user.id
    db = database.Connect(uid)
    class_ = db.get_class()
    del db