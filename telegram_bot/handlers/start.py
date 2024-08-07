from aiogram import types
from aiogram.dispatcher import Dispatcher

async def send_welcome(message: types.Message):
    await message.reply("Hi! Please upload a document to translate.")

def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
