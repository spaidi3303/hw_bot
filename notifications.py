from datetime import datetime, timedelta
import json
from queue import Empty

from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder

from database import Connect


async def send_homework(bot: Bot):
    db = Connect(0)
    all_ids = db.get_all_id()
    for uid in all_ids:
        class_name = db.get_class_id(uid)
        tomorrow = datetime.now() + timedelta(days=1)
        homeworks = db.get_all_homework(class_name, tomorrow.strftime('%d.%m'))
        res = []
        for lesson, hw in homeworks.items():
            res.append(f'{lesson} - {hw}')
        if res:
            for i in res:
                text = f"{i[:i.index("-")-1]}:"
                hw = i[i.index("-")+2:]
                array_hw = json.loads(hw.replace("'", '"'))
                if any(isinstance(item, list) for item in array_hw):
                    photo_ids = []
                    for j in array_hw:
                        if isinstance(j, str):
                            text += f"\n- {j}"
                        elif isinstance(j, list):
                            for file_id in j:
                                photo_ids.append(file_id)
                    if photo_ids is not Empty:
                        album_builder = MediaGroupBuilder(
                            caption=text
                        )
                        for fi_id in photo_ids:
                            album_builder.add_photo(
                                media=fi_id
                            )
                        await bot.send_media_group(
                            uid,
                            media=album_builder.build()
                        )

                else:
                    for j in array_hw:
                        text += f"\n- {j}"
                    else:
                        await bot.send_message(uid, text)
        else:
            await bot.send_message(uid, 'На завтра нет дз')
