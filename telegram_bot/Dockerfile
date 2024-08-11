# Dockerfile for the Telegram bot
FROM python:3.8-slim

WORKDIR /telegram_bot

COPY . /telegram_bot

RUN pip install -r requirements.txt

CMD ["python", "start_bot.py"]
