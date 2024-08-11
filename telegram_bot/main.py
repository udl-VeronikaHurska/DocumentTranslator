import logging
from aiogram.utils import executor
from bot_setup import dp
from handlers import register_handlers

logging.basicConfig(level=logging.INFO)

register_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
