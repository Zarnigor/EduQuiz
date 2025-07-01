import os, re, asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from together import Together
from feedback import analyze_and_feedback

# ─── API kaliti ───────────────────────────────────────────
load_dotenv()
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

users: dict[int, dict] = {}

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users[chat_id] = {}
    await update.message.reply_text("📚 Qaysi mavzuda test olmoqchisiz?")

async def receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    users[chat_id] = {"subject": text}     

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🟢 Oson", callback_data="oson"),
        InlineKeyboardButton("🟡 O‘rta", callback_data="o‘rta"),
        InlineKeyboardButton("🔴 Qiyin", callback_data="qiyin"),
    ]])

    await update.message.reply_text(
        "✅ Mavzu qabul qilindi!\nDarajani tanlang:",
        reply_markup=keyboard,
    )

async def receive_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    diff = query.data                          # 'oson' | 'o‘rta' | 'qiyin'
    subject = users.get(chat_id, {}).get("subject")

    if not subject:                            
        await query.message.reply_text("Avval test mavzusini yuboring. /start bilan boshlaymiz.")
        return

    await query.edit_message_reply_markup()    
    await query.message.reply_text("🔄 Savollar tayyorlanmoqda…")

    q, c = await generate_quiz(subject, diff)  # AI dan savollar
    users[chat_id].update({
        "questions": q,
        "correct": c,
        "current": 0,
        "user_ans": [],
    })

    await send_poll_question(query.message.chat, context)

async def generate_quiz(subject: str, difficulty: str):
    prompt = (
        f"Menga {subject} bo‘yicha {difficulty} darajada 10 ta test savol tuzib ber. "
        "Har bir savolga 4 ta variant (A, B, C, D) bo‘lsin. "
        "Hamma savollardan so‘ng 'A, B …' ko‘rinishida faqat to‘g‘ri javoblarni yoz. Javoblar deb yozish ham shart emas."
        "Hech qanday boshqa matn yozma. ** va boshqa markdown belgilardan ham foydalanma"
    )
    resp = await asyncio.to_thread(
        lambda: client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
    )
    parts = resp.choices[0].message.content.strip().split("\n\n")
    questions, answers_line = parts[:-1], parts[-1]
    print(questions, answers_line)
    correct = [c.upper() for c in answers_line.split(", ")]

    if len(questions) != 10 or len(correct) != 10:
        raise ValueError("AI noto‘g‘ri format yubordi")
    return questions, correct


async def send_poll_question(chat, context: ContextTypes.DEFAULT_TYPE):
    chat_id = chat.id
    i = users[chat_id]["current"]
    q_raw = users[chat_id]["questions"][i]

    lines = [l.strip() for l in q_raw.splitlines() if l.strip()]
    q_text, opts_raw = lines[0], lines[1:]
    opts = [re.sub(r"^[A-D]\\s*[.)-]?\\s*", "", o) for o in opts_raw]
    correct_idx = "ABCD".index(users[chat_id]["correct"][i])

    poll = await context.bot.send_poll(
        chat_id=chat_id,
        question=f"❓ Savol {i+1}:\n{q_text}",
        options=[f"{opts[0]}", f"{opts[1]}", f"{opts[2]}", f"{opts[3]}"],
        type="quiz",
        correct_option_id=correct_idx,
        is_anonymous=False,
    )

    context.bot_data[poll.poll.id] = {"chat_id": chat_id}
    users[chat_id]["current"] += 1

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = update.poll_answer.poll_id
    chat_id = context.bot_data[poll_id]["chat_id"]
    chosen = update.poll_answer.option_ids[0]

    users[chat_id]["user_ans"].append("ABCD"[chosen])

    if users[chat_id]["current"] < 10:
        chat = await context.bot.get_chat(chat_id)
        await send_poll_question(chat, context)
    else:
        chat = await context.bot.get_chat(chat_id)
        await analyze_and_feedback(chat, users[chat_id], context)

__all__ = [
    "start_quiz",
    "receive_topic",
    "receive_difficulty",
    "handle_poll_answer",
]
