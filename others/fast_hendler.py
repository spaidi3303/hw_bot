from aiogram import Router, F, types

import database
from others.constants import OWN_ID

router = Router()

db = database.Connect(1)
all_id = db.get_all_id()
del db

@router.message(lambda message: str(message.from_user.id) not in all_id)
async def ban_user(ms: types.Message):
    ...


@router.message(F.text.lower() == "пользователи", F.from_user.id.in_(OWN_ID))
async def list_users(ms: types.Message):
    db = database.Connect(1)
    all_id = db.get_all_id()
    del db
    text = ""
    ten_a = ""
    ten_b = ""
    ten_v = ""
    for i in all_id:
        user = await ms.bot.get_chat(i)
        mention_text = f"<a href='tg://user?id={user.id}'>{i}</a>"
        if i == '7778655804':
            continue

        db = database.Connect(i)
        class_ = db.get_class()
        del db
        if class_ == "10_a":
            ten_a += f"{mention_text} - {class_}\n"
        elif class_ == "10_b":
            ten_b += f"{mention_text} - {class_}\n"
        else:
            ten_v += f"{mention_text} - {class_}\n"
    text += ten_a
    text += ten_b
    text += ten_v
    await ms.answer(text)