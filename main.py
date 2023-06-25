import asyncio

import aioschedule
from aiogram import executor
from loguru import logger

from functions import dp
from functions.DB.current_orders import add_info_to_current_orders_from_sheet
from functions.DB.paid_db import clear_all_db


async def scheduler():
    aioschedule.every(10).seconds.do(add_info_to_current_orders_from_sheet)
    aioschedule.every().day.at("1:00").do(clear_all_db)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())
    logger.add("logs/logging_info.log", rotation="1 week", retention="1 month", compression="zip",
               format="{time:HH:mm:ss} {level} {name} {function} {line} {message} ")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
