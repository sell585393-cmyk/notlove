# NOTLOVE.ME — Telegram-бот

Бот для 30-дневного вызова. Тёмное зеркало, ежедневные чек-ины, пиксельный двойник.

## Быстрый старт

1. Создай бота через [@BotFather](https://t.me/BotFather)
2. Скопируй токен
3. Настрой `.env`:

```bash
cp .env.example .env
# Вставь BOT_TOKEN и SUPABASE_KEY
```

4. Установи зависимости:

```bash
pip install -r requirements.txt
```

5. Применми миграцию к Supabase (или попроси Виктора)

6. Запусти:

```bash
python main.py
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать — приветствие, фото, выбор слабостей |
| `/checkin` | Дневной чек-ин |
| `/progress` | Мой прогресс |
| `/avatar` | Мой персонаж |
| `/settings` | Настройки |
| `/reset` | Сбросить и начать заново |

## Структура

```
bot/
├── main.py          — точка входа, запуск polling/webhook
├── config.py        — настройки, слабости, архетипы
├── handlers.py      — обработчики команд и callback'ов
├── keyboards.py     — клавиатуры и кнопки
├── texts.py         — все тексты бота
├── db.py            — работа с Supabase
├── avatar.py        — генерация пиксельного аватара
├── scheduler.py     — ежедневные напоминания
└── requirements.txt
```

## Режимы

- `python main.py` — long-polling (разработка)
- `python main.py webhook` — webhook (продакшн, нужен WEBHOOK_URL)
