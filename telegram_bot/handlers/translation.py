import logging
import requests
from aiogram import types
from io import BytesIO
from aiogram.dispatcher import Dispatcher
from settings import settings
from bot_setup import dp, bot
from aiogram.types import InputFile

async def handle_translation_option(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    file_data = user_data.get('file_data')
    file_name = user_data.get('file_name')

    if not file_data or not file_name:
        await message.reply("File data not found. Please upload the document again.")
        return

    src_lang, tgt_lang = settings.translation_options[message.text]

    # Prepare the file for upload to the translation API
    files = {'file': (file_name, file_data)}
    # logging.info(file_data)
    data = {'src_lang': src_lang, 'tgt_lang': tgt_lang,'output_format': 'docx'}
    # logging.info(data)
    # Send the file to the translation API
    try:
        response = requests.post(settings.TRANSLATION_API_URL, files=files, params=data)
        response.raise_for_status()

        # Receive the translated file
        translated_file = BytesIO(response.content)
        translated_file.name = f"translated_{file_name}"

        # Send the translated file back to the user
        await message.reply_document(InputFile(translated_file))

    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        await message.reply("An error occurred while translating the document. Please try again.")

def register_handlers_translation(dp: Dispatcher):
    dp.register_message_handler(handle_translation_option, lambda message: message.text in settings.translation_options.keys())
