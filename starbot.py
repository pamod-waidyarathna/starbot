from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, LabeledPrice
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, PreCheckoutQueryHandler
)

import os

TOKEN = os.getenv("BOT_TOKEN")

from catalog import VIDEOS, THUMBNAILS\n\nasync def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=THUMBNAILS[data],
            caption=f"🎬 {video['title']}\n💰 Price: {video['price']}⭐",
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
