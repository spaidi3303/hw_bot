from aiogram import Router, F, types

import database

router = Router()


@router.message((F.from_user.id == 6068641104))
async def ban_user(ms: types.Message):
    ...


@router.message(F.text.lower() == "пользователи", F.from_user.id == 2098644058)
async def list_users(ms: types.Message):
    db = database.Connect(2098644058)
    all_id = db.get_all_id()
    del db
    text = ""
    for i in all_id:
        db = database.Connect(i)
        text += f"{i} - {db.get_class()}\n"
        del db
    await ms.answer(text)