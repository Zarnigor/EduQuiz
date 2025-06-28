import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from dotenv import load_dotenv
load_dotenv()

ASK_TOPIC, ASK_DIFFICULTY = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Menga biror mavzu yubor va men savollar tuzaman!\n"
        "Iltimos, test mavzusini kiriting:"
    )
    return ASK_TOPIC

async def receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subject = update.message.text
    context.user_data["subject"] = subject
    await update.message.reply_text(
        f"Mavzu qabul qilindi: {subject}\n\n"
        "Endi qiyinchilik darajasini tanlang:\n"
        "1️⃣ Oson\n2️⃣ O‘rta\n3️⃣ Qiyin\n\n"
        "Faqat raqam kiriting (1, 2, yoki 3):"
    )
    return ASK_DIFFICULTY

async def receive_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    level_map = {
        "1": "oson",
        "2": "o‘rta",
        "3": "qiyin",
        "oson": "oson",
        "o‘rta": "o‘rta",
        "orta": "o‘rta",
        "qiyin": "qiyin",
    }

    if text not in level_map:
        await update.message.reply_text("⚠️ Iltimos, darajani 1, 2, 3 yoki matn shaklida kiriting (masalan: oson)")
        return ASK_DIFFICULTY

    difficulty = level_map[text]
    context.user_data["difficulty"] = difficulty
    subject = context.user_data["subject"]

    await update.message.reply_text(
        f"✅ Qabul qilindi:\nMavzu: {subject}\nDaraja: {difficulty.capitalize()}"
    )

    # Keyingi bosqich: AI dan savollar olish
    return ConversationHandler.END

topic_conversation = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic)],
        ASK_DIFFICULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_difficulty)],
    },
    fallbacks=[]
)

app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
app.add_handler(topic_conversation)
app.run_polling()
