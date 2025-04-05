from aiogram import Router

import add.add_homework as add_homework
import others.fast_hendler as fast_hendler
import get.get_homework as get_homework
import others.help as help
import get.last_marks as last_marks
import add.photo_save as photo_save
import others.start as start

router = Router()
router.include_router(fast_hendler.router)
router.include_router(add_homework.router)
router.include_router(get_homework.router)
router.include_router(help.router)
router.include_router(start.router)
router.include_router(last_marks.router)
router.include_router(photo_save.router)
