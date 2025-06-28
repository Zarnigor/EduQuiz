import os, dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, PollAnswerHandler,
    ConversationHandler, ContextTypes, filters,
)
from quiz import (
    ASK_TOPIC, ASK_DIFFICULTY, ASK_POLL,
    receive_topic, receive_difficulty,
    send_poll_question, handle_poll_answer,
)
dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Mavzuni kiriting:")
    return ASK_TOPIC

conv = ConversationHandler(
    entry_points=[CommandHandler("start", cmd_start)],
    states={
        ASK_TOPIC:      [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic)],
        ASK_DIFFICULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_difficulty)],
        ASK_POLL:       [],   # PollAnswerHandler ishlaydi
    },
    fallbacks=[],
)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(conv)
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    print("🤖 EduQuiz bot tayyor!")
    app.run_polling()

if __name__ == "__main__":
    main()
