from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils import markdown as md

from others_func import is_admin

router = Router()

HW_GET_HELP = f'''{md.bold('Получение домашки:')}

{md.code('дз')} \\- получить всю домашку на завтра
{md.code('дз число')} \\- получить домашку на указанное число\\*
{md.code('дз день недели')} \\- получить домашку на указанный день недели
{md.code('дз предмет')} \\- получить домашку на указанный предмет \\(откроется выбор даты\\)
'''

HW_ADD_HELP = f'''{md.bold('Добавление домашки:')}

{md.code('предмет - текст')} \\- добавить домашку по указанному предмету на ближайщий день с ним
{md.code('предмет число - текст')} \\- добавить домашку по указанному предмету на число\\*
{md.code('предмет день недели - текст')} \\- добавить домашку по указанному предмету на ближайщий день указанный день недели

{md.code('фотография (предмет)')} \\- добавить домашку фото по указанному предмету на ближайщий день с ним
{md.code('фотография (предмет число)')} \\- добавить домашку по указанному предмету на число\\*
{md.code('фотография (предмет день недели)')} \\- добавить домашку фото по указанному предмету на ближайщий день указанный день недели
'''

GET_MARKS_HELP = f'''{md.bold('Получение оценок:')}

{md.code('оценки')} или /marks \\- получить оценки \\(если эта команда ещё не выполнялась, бот предложит ввести логин и пароль от дневника\\)
{md.code('все оценки')} или /allmarks \\- получить все оценки по предметам в этом триместре
'''

NOTE = f'\\* формат \\- {md.code('день.месяц')}, например, {md.code('09.03')}'

USER_HELP = f'{HW_GET_HELP}\n{GET_MARKS_HELP}\n{NOTE}'

ADMIN_HELP = f'{HW_GET_HELP}\n{HW_ADD_HELP}\n{GET_MARKS_HELP}\n{NOTE}'


@router.message(F.text == '/help')
async def doc(message: Message):
    if is_admin(message.from_user.id):
        await message.answer(ADMIN_HELP, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await message.answer(USER_HELP, parse_mode=ParseMode.MARKDOWN_V2)
