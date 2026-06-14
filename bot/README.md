# 🤖 NOTLOVE.ME — Telegram-бот

Ядро проекта. Бот ведёт пользователя через онбординг, генерирует пиксельного двойника и проводит 30-дневный вызов.

## Файлы

| Файл | Описание |
|------|----------|
| `main.py` | Точка входа. Long-polling (dev) или webhook (prod). Запускает планировщик напоминаний. |
| `handlers.py` | Все обработчики: `/start`, фото, выбор слабостей, чек-ины, прогресс, персонаж, сброс. FSM на aiogram. |
| `avatar.py` | Генерация пиксельных аватаров через OpenAI Images API (`gpt-image-2`). С фото (edits) и без (generations). |
| `config.py` | Конфигурация из `.env`. Словари слабостей и архетипов. |
| `db.py` | Supabase-клиент: CRUD для users, weaknesses, challenges, checkins. Загрузка медиа в Storage. |
| `keyboards.py` | Все клавиатуры: главное меню (с кнопкой мини-аппы), выбор слабостей, чек-ин, подтверждения. |
| `texts.py` | Все тексты бота на русском. Мотивационные фразы, прогресс-бар. |
| `scheduler.py` | Ежедневные напоминания в 20:00 МСК для тех, кто не отчитался. |

## Установка

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Скопировать и заполнить .env
cp .env.example .env
```

## Переменные окружения

```env
# Telegram Bot API токен от @BotFather
BOT_TOKEN=

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJ...  # anon/service key

# OpenAI API (для генерации аватаров)
OPENAI_API_KEY=sk-...

# Telegram Mini App URL
MINI_APP_URL=https://notlove-me.vercel.app/app

# Webhook (для продакшна, необязательно)
WEBHOOK_URL=
WEBHOOK_PORT=8443
```

## Запуск

```bash
# Разработка (long-polling)
python main.py

# Продакшн (webhook)
python main.py webhook
```

## FSM-цепочка онбординга

```
[/start]
    │
    ▼
Onboarding.waiting_photo
    │
    ├── Отправил фото → сохраняем в Supabase Storage
    │   │
    │   ▼
    └── Пропустил
        │
        ▼
Onboarding.choosing_weaknesses
    │
    ├── Тогглит слабости (до 6 из 6)
    │
    └── «Готово»
        │
        ├── Сохраняет слабости в БД
        ├── Определяет архетип
        ├── Вызывает OpenAI → генерирует аватар
        ├── Загружает аватар в Supabase Storage
        │
        ▼
Onboarding.confirming
    │
    ├── «Начать 30 дней» → создаёт challenge → main_menu
    └── «Пока нет» → выход
```

## Чек-ин (ежедневный)

```
[✅ Чек-ин]
    │
    ▼
CheckinFlow.answering
    │
    ├── По каждой слабости: ✅ держался / ❌ сорвался
    │
    └── «Отправить чек-ин»
        │
        ├── Все держался → стрик +1
        └── Есть срыв → стрик = 0
```

## Генерация аватаров (`avatar.py`)

- **С фото:** `POST /v1/images/edits` — трансформирует реальное фото в пиксельного персонажа
- **Без фото:** `POST /v1/images/generations` — генерирует дефолтного персонажа
- **Модель:** `gpt-image-2`
- **Размер:** 1024×1536 (портрет 2:3)
- **Стиль:** Lisa: The Painful RPG, CRT scanlines, тёмная палитра
- **Слабости влияют** на body language и атмосферу

## Деплой на VPS

```bash
# Копируем все .py файлы
scp *.py user@server:/opt/notlove-bot/

# Рестарт сервиса
ssh user@server "systemctl restart notlove-bot"

# Проверка
ssh user@server "systemctl status notlove-bot"
ssh user@server "journalctl -u notlove-bot -n 20 --no-pager"
```

### systemd unit (`/etc/systemd/system/notlove-bot.service`)

```ini
[Unit]
Description=NOTLOVE.ME Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/notlove-bot
ExecStart=/opt/notlove-bot/venv/bin/python main.py
Restart=always
RestartSec=5
EnvironmentFile=/opt/notlove-bot/.env

[Install]
WantedBy=multi-user.target
```

## Зависимости

```
aiogram==3.18.0      # Telegram Bot Framework
aiohttp==3.11.18     # HTTP-сервер для webhook
supabase==2.15.2     # Supabase Python клиент
python-dotenv==1.1.0 # .env файлы
Pillow==11.2.1       # Обработка изображений
httpx==0.28.1        # Async HTTP-клиент (для OpenAI API)
```
