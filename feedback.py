import asyncio
from telegram.constants import ParseMode

# MarkdownV2 escape
def esc_md(text: str) -> str:
    for ch in r'\_*[]()~`>#+-=|{}.!':
        text = text.replace(ch, f'\\{ch}')
    return text

async def analyze_and_feedback(chat, context, client):
    q, user, corr = context.user_data["questions"], context.user_data["user_ans"], context.user_data["correct"]
    prompt = "Noto‘g‘ri javoblar bo‘yicha qisqa tushuntirish ber:\n\n Sen userga yozasan, muloyim bo'l. Hech qanday markdownlardan foydalanmang yaxshiroq"
    for i, (qq, c, u) in enumerate(zip(q, corr, user), 1):
        prompt += f"{i}) {qq}\nTo‘g‘ri: {c} | Foydalanuvchi: {u}\n\n"

    resp = await asyncio.to_thread(
        lambda: client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
    )
    fb = esc_md(resp.choices[0].message.content.strip())
    score = sum(u == c for u, c in zip(user, corr))
    text = esc_md(f"🏁 Test tugadi!\nBall: {score}/10\n\n🧠 Feedback:\n{fb}")

    await chat.send_message(text=text, parse_mode=ParseMode.MARKDOWN_V2)
