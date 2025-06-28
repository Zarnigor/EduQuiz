# EduQuiz‑AI 🤖

![GitHub](https://img.shields.io/github/license/Zarnigor/EduQuizBot?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)
![Telegram Bot](https://img.shields.io/badge/telegram-bot-blue?logo=telegram\&style=flat-square)
![Together AI](https://img.shields.io/badge/Together.ai-powered-orange?style=flat-square)

> **AI‑quvvatlangan interaktiv test bot** – Telegram’da mavzu va darajani tanlang, 10 ta avtomatik quiz o‘ynang va darhol xatolaringiz bo‘yicha tavsiyalar oling.

---

## 📚 Jadval

1. [Xususiyatlar](#xususiyatlar)
2. [Demo](#demo)
3. [O‘rnatish](#o-rnatish)
4. [Foydalanish](#foydalanish)
5. [Texnologiyalar](#texnologiyalar)
6. [Struktura](#loyiha-struktura-si)

---

## Xususiyatlar

|                                            |                                                                               |
| ------------------------------------------ | ----------------------------------------------------------------------------- |
| **AI savol generator**                     | Together AI (`DeepSeek‑V3`) modeli mavzu + daraja asosida 10 ta test yaratadi |
| **Quiz Poll UI**                           | Har savol Telegram’ning *Quiz Poll* formatida, to‘g‘ri javob yashirin         |
| **Avtomatik baholash**                     | 10 ta javob yig‘iladi, ball hisoblanadi                                       |
| **AI feedback**                            | Faqat xato javoblar bo‘yicha qisqa tushuntirish va tavsiyalar                 |
| **Hech qanday markdown belgisiz feedback** | `parse_mode=HTML`: xatoliklar formatlanmaydi                                  |

---

## Demo

<div align="center">
  <img src="https://raw.githubusercontent.com/Zarnigor/EduQuizBot/assets/demo.gif" alt="EduQuiz demo" width="500"/>
</div>

---

## O‘rnatish

```bash
# klonlash
$ git clone https://github.com/Zarnigor/EduQuizBot.git && cd EduQuizBot

# virtual muhit
$ python -m venv .venv && source .venv/bin/activate

# kutubxonalar
$ pip install -r requirements.txt

# .env faylini yaratish
$ cp .env.example .env
$ nano .env   # TOKEN va TOGETHER_API_KEY ni kiriting
```

---

## Foydalanish

```bash
python main.py
```

Telegram’da botga `/start` yozing → mavzu va darajani tanlang → savollarni ishlang.

---

## Texnologiyalar

* **Python 3.10 +**
* [python‑telegram‑bot v20](https://docs.python-telegram-bot.org/) – bot framework
* [Together AI](https://www.together.ai/) – DeepSeek‑V3 LLM
* **dotenv** – maxfiy kalitlarni .env orqali saqlash

---

## Loyiha struktura‑si

```text
EduQuizBot/
├── main.py          # ishga tushiruvchi fayl
├── quiz.py          # AI generator, poll va feedback logikasi
├── requirements.txt # paketlar ro‘yxati
├── .env.example     # namuna maxfiy o‘zgaruvchilar
└── README.md        # shu hujjat
```

