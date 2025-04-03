from aiogram import Router

import add_homework
import fast_hendler
import get_homework
import get_homework_keyboard
import help
import last_marks
import photo_save
import start

router = Router()
router.include_router(fast_hendler.router)
router.include_router(add_homework.router)
router.include_router(get_homework.router)
router.include_router(get_homework_keyboard.router)
router.include_router(help.router)
router.include_router(start.router)
router.include_router(last_marks.router)
router.include_router(photo_save.router)
