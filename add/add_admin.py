from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder, InlineKeyboardButton

import database


router = Router()

@router.message(F.contact)
async def add_contact(ms: types.Message):
    uid = ms.from_user.id
    db = database.Connect(uid)
    if ms.contact.user_id in db.get_admins()['admins']:
        await ms.answer("Админ уже добавлен. Желаете его удалить?", reply_markup=await deladm_buttons(ms.contact.user_id))
        return
    own = db.get_admins()['own']
    if uid != own:
        await ms.answer("Добавлять админов может только староста!")
        return
    db.add_admin(ms.contact.user_id)
    await ms.answer("Админ был добавлен!")


class AdminDel(CallbackData, prefix="deladm"):
    id: int
    action: str

async def deladm_buttons(uid: int):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Да", callback_data=AdminDel(id=uid, action="yes").pack()))
    builder.add(InlineKeyboardButton(text="Нет", callback_data=AdminDel(id=uid, action="no").pack()))
    builder.adjust(2)
    return builder.as_markup()

@router.callback_query(AdminDel.filter())
async def del_adm_yes(query: CallbackQuery, callback_data: AdminDel):
    if callback_data.action == "yes":
        uid = callback_data.id
        db = database.Connect(uid)
        db.del_admin(uid)
        await query.message.edit_text("Админ был удалён")
    elif callback_data.action == "no":
        await query.message.edit_text("Админ был оставлен")