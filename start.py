from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder, InlineKeyboardButton

from aiogram.enums.parse_mode import ParseMode
import database
from help import FULL_HELP, HELP
from others_func import is_admin

router = Router()
block_user = [6068641104, 7778655804]
CLASSES = {
    '10А': '10_a',
    '10Б': '10_b',
    '10В': '10_v'
}


class ActionListClasses(CallbackData, prefix="class"):
    id: int
    class_name: str

@router.message(F.text == "/start")
async def start(message: Message):
    db = database.Connect(message.from_user.id)
    if db.user_exists():
        if is_admin(message.from_user.id):
            await message.answer(FULL_HELP, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await message.answer(HELP, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        
        await message.answer('Привет! Выбери свой класс:',
                             reply_markup=await classes_buttons(message.from_user.id))


@router.callback_query(ActionListClasses.filter())
async def on_class_choice(query: CallbackQuery, callback_data: ActionListClasses):
    db = database.Connect(callback_data.id)
    db.create_user(callback_data.class_name)
    await query.message.edit_text('Регистрация прошла успешно. Можно начинать пользоваться ботом.')


async def classes_buttons(uid: int):
    builder = InlineKeyboardBuilder()
    for class_name, class_name_prog in CLASSES.items():
        builder.row(InlineKeyboardButton(text=class_name,
                                         callback_data=ActionListClasses(id=uid, class_name=class_name_prog).pack()
                                        )
                    )
    builder.adjust(2)
    return builder.as_markup()
