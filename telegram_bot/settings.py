import os
class Settings():
    TRANSLATION_API_URL: str = 'http://translator_backend:8000/translate_document'
    translation_options: dict = {
    '/ua_en':('ukrainian', 'english'),
    '/de_ua': ('german', 'ukrainian'),
    '/en_ua': ('english', 'ukrainian'),
    '/ua_de':('ukrainian', 'german'),
    '/de_en':('german', 'english'),
    '/en_de':('english', 'german')
}
    TELEGRAM_BOT_TOKEN:str =  os.getenv("TELEGRAM_BOT_TOKEN")



settings = Settings()