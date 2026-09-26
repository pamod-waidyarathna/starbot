import asyncio
import os
import sys

from flask import Flask, request
from telegram import Update

PROJECT_HOME = "/home/pamod/starbot"
if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

ENV_FILE = os.path.join(PROJECT_HOME, ".env")
if os.path.isfile(ENV_FILE):
    with open(ENV_FILE, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

from starbot import build_application

application = Flask(__name__)


async def process_telegram_update(payload):
    telegram_app = build_application()

    # PythonAnywhere WSGI web apps do not support background threads.
    # Process each Telegram update synchronously inside this request instead.
    await telegram_app.initialize()
    try:
        update = Update.de_json(payload, telegram_app.bot)
        await telegram_app.process_update(update)
    finally:
        await telegram_app.shutdown()


@application.get("/")
def home():
    return "StarBot server works!"


@application.post("/telegram")
def telegram_webhook():
    payload = request.get_json(force=True, silent=False)
    asyncio.run(process_telegram_update(payload))
    return "OK", 200
