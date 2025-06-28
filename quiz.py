import os, re, asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from together import Together
from feedback import analyze_and_feedback

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

# Conversation states
ASK_TOPIC, ASK_DIFFICULTY, ASK_POLL = range(3)

# ─────────────────────────  AI savollar  ─────────────────────────
async def generate_quiz(subject: str, difficulty: str):
    prompt = (
        f"Menga {subject} bo‘yicha {difficulty} darajada 10 ta test savol tuzib ber. "
        "Har bir savolga 4 ta variant (A, B, C, D) bo‘lsin. "
        "Savollardan so‘ng 'A, B …' ko‘rinishida faqat to‘g‘ri javoblarni yoz. Javoblar deb yozish ham shart emas."
        "Hech qanday boshqa matn yozma."
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

# ──────────  Topic va difficulty qabul  ──────────
async def receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subject"] = update.message.text.strip()
    await update.message.reply_text(
        "Darajani tanlang:\n1️⃣ Oson  2️⃣ O‘rta  3️⃣ Qiyin (1/2/3):"
    )
    return ASK_DIFFICULTY

async def receive_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    level_map = {"1": "oson", "2": "o‘rta", "3": "qiyin"}
    diff = level_map.get(update.message.text.strip())
    if not diff:
        await update.message.reply_text("Faqat 1, 2 yoki 3 ni kiriting.")
        return ASK_DIFFICULTY

    await update.message.reply_text("🔄 Savollar tayyorlanmoqda…")
    q, c = await generate_quiz(context.user_data["subject"], diff)
    context.user_data.update({"questions": q, "correct": c, "current": 0, "user_ans": []})
    return await send_poll_question(update, context)

# ──────────  Poll‑quiz yuborish  ──────────
async def send_poll_question(update_or_chat, context: ContextTypes.DEFAULT_TYPE):
    i = context.user_data["current"]
    q_raw = context.user_data["questions"][i]
    lines = [l.strip() for l in q_raw.splitlines() if l.strip()]
    q_text, opts_raw = lines[0], lines[1:]
    opts = [re.sub(r"^[A-D]\s*[.)-]?\s*", "", o) for o in opts_raw]

    correct_idx = "ABCD".index(context.user_data["correct"][i])
    chat_id = update_or_chat.effective_chat.id if isinstance(update_or_chat, Update) else update_or_chat.id

    poll = await context.bot.send_poll(
        chat_id=chat_id,
        question=f"❓ Savol {i+1}:\n{q_text}",
        options=[f"A) {opts[0]}", f"B) {opts[1]}", f"C) {opts[2]}", f"D) {opts[3]}"],
        type="quiz",
        correct_option_id=correct_idx,
        is_anonymous=False,
    )
    context.bot_data[poll.poll.id] = {"chat_id": chat_id}
    context.user_data["current"] += 1
    return ASK_POLL

# ──────────  Poll‑javobni qayta ishlash  ──────────
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = update.poll_answer.poll_id
    if poll_id not in context.bot_data:
        return
    chosen = update.poll_answer.option_ids[0]
    context.user_data["user_ans"].append("ABCD"[chosen])

    if context.user_data["current"] < 10:
        chat = await context.bot.get_chat(context.bot_data[poll_id]["chat_id"])
        await send_poll_question(chat, context)
    else:
        chat = await context.bot.get_chat(context.bot_data[poll_id]["chat_id"])
        await analyze_and_feedback(chat, context, client)   # <– feedback.py funksiyasi
