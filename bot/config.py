"""Конфигурация бота NOTLOVE.ME"""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wfkplqgufdaxnczvyhpn.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://notlove-me.vercel.app/app")

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))

# 30-дневный вызов
CHALLENGE_DAYS = 30

# Слабости
WEAKNESSES = {
    "sleep":  {"label": "Сон",    "emoji": "🌙", "desc": "Ложишься когда придётся, встаёшь никакой"},
    "feed":   {"label": "Лента",  "emoji": "📱", "desc": "Часы уходят в чужие жизни"},
    "porn":   {"label": "18+",    "emoji": "🔞", "desc": "Каждый вечер одно и то же"},
    "food":   {"label": "Еда",    "emoji": "🍔", "desc": "Топливо из помойки"},
    "gym":    {"label": "Тело",   "emoji": "🏋️", "desc": "Ни разу не встал ради себя"},
    "money":  {"label": "Деньги", "emoji": "💸", "desc": "Тратишь на мусор, копишь на ничего"},
}

# Архетипы
ARCHETYPES = {
    "slug":      {"label": "Сутулый Слизень",  "desc": "Сидячий, телефон, ноль режима"},
    "gladiator": {"label": "Сырой Гладиатор",  "desc": "Потенциал есть, дисциплины нет"},
    "boss":      {"label": "Жирный Босс",      "desc": "Деньги/еда/стресс, надо резать лишнее"},
    "demon":     {"label": "Ночной Демон",      "desc": "Сон убит, думскролл, хаос"},
    "empty":     {"label": "Пустой Качок",      "desc": "Форма есть, но режим ломает прогресс"},
}
