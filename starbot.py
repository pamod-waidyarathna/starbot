from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, LabeledPrice
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, PreCheckoutQueryHandler
)
from telegram.error import TelegramError

import os

TOKEN = os.getenv("BOT_TOKEN")

# ---------- VIDEOS ----------
VIDEOS = {
    "v1": {"title": "Video 1", "file_id": "BAACAgUAAxkBAAEq9ERqNh7qP382KtYEw_vj_d1R7VJkGAACkgkAAsEW4VYGOhxpUoa1yDwE", "price": 1},
    "v2": {"title": "Video 2", "file_id": "BAACAgUAAxkBAAEq9EVqNh7qB5dZ0Aj3YPx5uxNLk3UQ9wAC2BAAAqjw8VXFGmPVocXyajwE", "price": 40},
    "v3": {"title": "Video 3", "file_id": "BAACAgUAAxkBAAEq9EdqNh7qbNlWxdKfZNGT21PnaUu2BwAC8Q8AArRQ6Vd--h_fdfaCRjwE", "price": 50},
    "v4": {"title": "Video 4", "file_id": "BAACAgUAAxkBAAEq9EZqNh7q2fKsD4jCsQnOw7IpIehBqQACrg8AAqLTmFWb-JYgnL_gjjwE", "price": 60},
    "v5": {"title": "Video 5", "file_id": "BAACAgUAAxkBAAEq9ElqNh7qv0gfnUK2Ow1BAcAFnmFNyQAClAoAAqVAcVb0eR9RqCR-8TwE", "price": 70},
}

THUMBNAILS = {
    "v1": "AgACAgUAAxkBAANPajd1WMlJUI-N_TU1mquHRXgYWRQAAnISaxs7ZLlV_aPW-5jrtp4BAAMCAAN4AAM8BA",
    "v2": "AgACAgUAAxkBAANLajdzKZCgcK9I4iGBRpRpHeThovMAAq4SaxsU0MFVEVNTYg4I-VkBAAMCAAN4AAM8BA",
    "v3": "AgACAgUAAxkBAANMajdzKUnqttIedXn3cgElvsuYeUMAAq8SaxsU0MFVroHDGwP75pYBAAMCAAN4AAM8BA",
    "v4": "AgACAgUAAxkBAANNajdzKZBfcsw3YuQu6Diso5t1XsUAArASaxsU0MFVsBXqYsx9IAYBAAMCAAN4AAM8BA",
    "v5": "AgACAgUAAxkBAANOajdzKXDvYpHwMuiJEWMPBCIem6oAArESaxsU0MFVlunKRUywkVYBAAMCAAN4AAM8BA",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎬 Catalog"], ["⚙️ Settings", "🛒 My cart"], ["💬 Support"]]
    await update.message.reply_text(
        "🎥 Mini Punishment video Store\nChoose option:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎬 Catalog":
        keyboard = [
            [InlineKeyboardButton("🎬 Video 1", callback_data="v1"),
             InlineKeyboardButton("🎬 Video 2", callback_data="v2")],
            [InlineKeyboardButton("🎬 Video 3", callback_data="v3"),
             InlineKeyboardButton("🎬 Video 4", callback_data="v4")],
            [InlineKeyboardButton("🎬 Video 5", callback_data="v5")]
        ]
        await update.message.reply_text(
            "📦 Choose a video:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif text == "⚙️ Settings":
        await update.message.reply_text("⚙️ Settings coming soon")
    elif text == "🛒 My cart":
        await update.message.reply_text("🛒 Cart is empty")
    elif text == "💬 Support":
        await update.message.reply_text(
            "💬 Contact: @idiot_siblings \nOur channel: https://t.me/+0nYyGFj9SSVhY2Q1"
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    print("CLICK:", data)

    if data in VIDEOS:
        video = VIDEOS[data]
        keyboard = [[InlineKeyboardButton(
            f"💰 Buy - {video['price']}⭐",
            callback_data=f"buy_{data}"
        )]]
        try:
            await context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=THUMBNAILS[data],
                caption=f"🎬 {video['title']}\n💰 Price: {video['price']}⭐",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except TelegramError as exc:
            print("THUMBNAIL ERROR:", repr(exc))
            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"🎬 {video['title']}\n💰 Price: {video['price']}⭐",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    elif data.startswith("buy_"):
        vid = data.replace("buy_", "")
        await context.bot.send_invoice(
            chat_id=query.message.chat.id,
            title=VIDEOS[vid]["title"],
            description="Lifetime access video",
            payload=vid,
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("Video", VIDEOS[vid]["price"])]
        )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vid = update.message.successful_payment.invoice_payload
    await update.message.reply_text("✔ Payment received. Sending video...")
    await update.message.reply_video(
        video=VIDEOS[vid]["file_id"],
        caption="🎬 Lifetime access unlocked"
    )

def build_application():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = Application.builder().token(TOKEN).updater(None).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, success))
    return app

# Kept for local/manual runs only. Importing this module no longer starts a server.
if __name__ == "__main__":
    app = build_application()
    print("BOT RUNNING ✔ (polling)")
    app.run_polling()
