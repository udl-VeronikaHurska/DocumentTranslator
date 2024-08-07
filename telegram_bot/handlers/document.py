import requests
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import Dispatcher
from settings import settings
from bot_setup import bot, dp
import os 

async def handle_docs(message: types.Message):
    document = message.document
    file_id = document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path

    # Download the file from Telegram
    file_url = f'https://api.telegram.org/file/bot{os.getenv("TELEGRAM_BOT_TOKEN")}/{file_path}'
    response = requests.get(file_url)
    file_data = response.content

    # Save file data to the user's state
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(file_data=file_data, file_name=document.file_name)

    # Create a keyboard with translation options
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for command in settings.translation_options.keys():
        keyboard.add(KeyboardButton(command))

    await message.reply("Please select a translation option:", reply_markup=keyboard)

def register_handlers_document(dp: Dispatcher):
    dp.register_message_handler(handle_docs, content_types=types.ContentType.DOCUMENT)
