import asyncio
import os
import sys
import threading
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

telegram_app = build_application()

_loop = asyncio.new_event_loop()

def _run_loop():
    asyncio.set_event_loop(_loop)
    _loop.run_forever()

_thread = threading.Thread(target=_run_loop, daemon=True)
_thread.start()

async def _initialize():
    await telegram_app.initialize()

asyncio.run_coroutine_threadsafe(_initialize(), _loop).result(timeout=20)

application = Flask(__name__)

@application.get("/")
def home():
    return "StarBot server works!"

@application.post("/telegram")
def telegram_webhook():
    payload = request.get_json(force=True, silent=False)
    update = Update.de_json(payload, telegram_app.bot)
    future = asyncio.run_coroutine_threadsafe(
        telegram_app.process_update(update),
        _loop
    )
    future.result(timeout=20)
    return "OK"
