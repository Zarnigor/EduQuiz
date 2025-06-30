from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PollAnswerHandler,
    filters,
)
from quiz import (
    start_quiz,
    receive_topic,
    receive_difficulty,
    handle_poll_answer,
)
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")          # .env dan yuklanadi

def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    # 1) /start → mavzuni so‘rash
    app.add_handler(CommandHandler("start", start_quiz))
    # 2) Foydalanuvchi mavzuni matn qilib yuboradi
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic))
    # 3) Tugma bosilganda (daraja)
    app.add_handler(CallbackQueryHandler(receive_difficulty))
    # 4) Poll javoblari
    app.add_handler(PollAnswerHandler(handle_poll_answer))

    print("✅ Bot ishga tushdi…")
    app.run_polling()

if __name__ == "__main__":
    main()
