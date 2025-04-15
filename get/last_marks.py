import asyncio
from enum import Enum
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder, InlineKeyboardButton
import re
from aiogram.fsm.context import FSMContext
import database
import others.parsing as parsing
from aiogram.enums import ChatAction
from aiogram.fsm.state import StatesGroup, State


class RegisterDnevnikState(StatesGroup):
    login = State()
    password = State()


router = Router()
# "27190", "862510"
@router.message((F.text.lower() == "оценки") | (F.text == "/marks"))
async def marks_give(ms: Message):
    asyncio.create_task(keep_action_alive(ms.chat.id, ms))
   
    db = database.Connect(ms.from_user.id)
    login, password = db.get_login_password()
    if login == '0':
        await ms.answer("Нужны ваши данные от дневника для просмотра оценок. "
        "Вы согласны предоставить эти данные чтобы пользоваться ботом? "
        "Логин и пароль будут зашифрованы и доступны только вам", reply_markup= await dnevnik_buttons())

    else:
        try:
            await ms.bot.send_chat_action(ms.chat.id, ChatAction.TYPING)
            res = await parsing.parse(login, password)
            text = ""
            for grade in res:
                date = re.findall(r"\d\d\.\d\d", grade[0])[0]
                text += f"{date} {grade[1]} - {grade[2]}\n"
            await ms.answer(text)
        finally:
            keep_action_alive.done = True

@router.message((F.text.lower() == "все оценки") | (F.text == "/allmarks"))
async def marks_all_give(ms: Message):
    asyncio.create_task(keep_action_alive(ms.chat.id, ms))
   
    db = database.Connect(ms.from_user.id)
    login, password = db.get_login_password()
    if login == '0':
        await ms.answer("Нужны ваши данные от дневника для просмотра оценок. "
        "Вы согласны предоставить эти данные чтобы пользоваться ботом? "
        "Логин и пароль будут зашифрованы и доступны только вам", reply_markup= await dnevnik_buttons())

    else:
        try:
            await ms.bot.send_chat_action(ms.chat.id, ChatAction.TYPING)
            res = await parsing.parse_all(login, password)
            text = ""
            for grade in res:
                text += f"\n\n{grade[0]}: {grade[1]}\n"
                for i in grade[2]:
                    text += f"{i} "
            await ms.answer(text)
        finally:
            keep_action_alive.done = True


async def keep_action_alive(chat_id: int, ms: Message):
    while not hasattr(keep_action_alive, "done"):
        await ms.bot.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(4) 


class DnevnikAction(Enum):
    yes = "yes"
    no = "no"


class ActionDnevnik(CallbackData, prefix="dnevnik"):
    action: DnevnikAction


async def dnevnik_buttons():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Да, я предоставлю", callback_data=ActionDnevnik(action=DnevnikAction.yes).pack()))
    builder.row(InlineKeyboardButton(text="Нет, я не дам эти данные", callback_data=ActionDnevnik(action=DnevnikAction.no).pack()))
    
    return builder.as_markup()


@router.callback_query(ActionDnevnik.filter(F.action == DnevnikAction.yes))
async def on_dnevnik_choice(query: CallbackQuery, callback_data: ActionDnevnik, state: FSMContext):
    await state.set_state(RegisterDnevnikState.login)
    await query.message.answer("Введи свой логин от дневника")


@router.message(RegisterDnevnikState.login, F.text.regexp(r"\d+"))
async def login_input(ms: Message, state: FSMContext):
    await ms.answer("Теперь введи пароль")
    await state.update_data(login=ms.text)
    await state.set_state(RegisterDnevnikState.password)


@router.message(RegisterDnevnikState.password, F.text.regexp(r"\d+"))
async def password_input(ms: Message, state: FSMContext):
    res = await state.update_data(password=ms.text)
    await state.clear()
    ps = await parsing.log_ps(res['login'], res['password'])
    keep_action_alive.done = True
    if ps:
        await ms.answer("Ваши данные были сохранены. Можете просматривать оценки")
        db = database.Connect(ms.from_user.id)
        db.update_login_password(res['login'], res['password'])
    else:
        await ms.answer("Ваши данные не коректны! Перепроверьте логин и пароль")
        await state.set_state(RegisterDnevnikState.login)
        await ms.answer("Введи свой логин от дневника")