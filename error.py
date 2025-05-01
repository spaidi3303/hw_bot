import logging
import traceback

from aiogram import Bot, Router, types

router = Router()


@router.error()
async def error_handler(event: types.ErrorEvent, bot: Bot):
    error = event.exception
    error_type = error.__class__.__name__
    error_message = str(event.update.message.text)

    # Получаем сокращенный traceback
    tb_list = traceback.format_exception(type(error), error, error.__traceback__)
    tb_short = "".join(tb_list[-2:])
    error_summary = (
        f"🚨 Ошибка:\n"
        f"• Тип: {error_type}\n"
        f"• Сообщение: {error_message}\n"
        f"• Место:\n{tb_short}"
    )
    logging.error(error_summary)
    await bot.send_message(2098644058, error_summary)
    return True
