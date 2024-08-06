import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import os
from io import BytesIO

# Telegram bot token
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize bot and dispatcher with memory storage
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# URL of the translation API endpoint
TRANSLATION_API_URL = 'http://translator_backend:8000/translate_document'

# Define translation options
translation_options = {
    '/de_ua': ('german', 'ukrainian'),
    '/en_ua': ('english', 'ukrainian'),
    '/ua_en':('ukrainian', 'english'),
    '/ua_de':('ukrainian', 'german'),
    '/de_en':('german', 'english'),
    '/en_de':('english', 'german')
}


# Handler for the /start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hi! Please upload a document to translate.")

# Handler for document upload
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_docs(message: types.Message):
    document = message.document
    file_id = document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path

    # Download the file from Telegram
    file_url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}'
    response = requests.get(file_url)
    file_data = response.content

    # Save file data to the user's state
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(file_data=file_data, file_name=document.file_name)

    # Create a keyboard with translation options
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for command in translation_options.keys():
        keyboard.add(KeyboardButton(command))

    await message.reply("Please select a translation option:", reply_markup=keyboard)

# Handler for translation options
@dp.message_handler(lambda message: message.text in translation_options.keys())
async def handle_translation_option(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    file_data = user_data.get('file_data')
    file_name = user_data.get('file_name')

    if not file_data or not file_name:
        await message.reply("File data not found. Please upload the document again.")
        return

    src_lang, tgt_lang = translation_options[message.text]

    # Prepare the file for upload to the translation API
    files = {'file': (file_name, file_data)}
    data = {'src_lang': src_lang, 'tgt_lang': tgt_lang, 'output_format': 'docx'}

    # Send the file to the translation API
    try:
        response = requests.post(TRANSLATION_API_URL, files=files, data=data)
        response.raise_for_status()

        # Receive the translated file
        translated_file = BytesIO(response.content)
        translated_file.name = f"translated_{file_name}"

        # Send the translated file back to the user
        await message.reply_document(InputFile(translated_file))

    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        await message.reply("An error occurred while translating the document. Please try again.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
