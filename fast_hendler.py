from aiogram import Router, F, types

router = Router()


@router.message((F.from_user.id == 6068641104))
async def ban_user(ms: types.Message):
    ...
