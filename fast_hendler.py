from aiogram import Router, F, types

router = Router()
block_user = [6068641104, 7778655804]


@router.message((F.from_user.id == 6068641104) | (F.from_user.id == 7778655804))
async def ban_user(ms: types.Message):
    ...
