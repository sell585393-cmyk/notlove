# 🪞 NOTLOVE.ME

**Приложение для людей, которые себя не любят.**

Не мотивашка. Не коуч. Жёсткое зеркало: ты понимаешь, что сам себя сливаешь — и получаешь 30-дневный вызов.

## Как это работает

```
Фото → Нейронка анализирует → Определяет твой тип →
→ Генерирует пиксельного двойника → 30-дневный вызов
```

1. **Скидываешь фото** — бот анализирует и определяет твой архетип
2. **Выбираешь слабости** — до 6 из списка (сон, лента, 18+, еда, тело, деньги)
3. **Получаешь пиксельного двойника** — GPT Image 2 генерирует персонажа в стиле Lisa: The Painful RPG
4. **30 дней чек-инов** — каждый день отвечаешь честно: держался или сорвался
5. **Персонаж эволюционирует** — стрик растёт → персонаж крепнет, срыв → деградация

## Стек

| Компонент | Технология |
|-----------|-----------|
| Telegram-бот | Python 3.12, aiogram 3.18 |
| Мини-аппа (TG Mini App) | React, TypeScript, Vite |
| Лендинг | Next.js (Viktor Spaces) |
| База данных | Supabase (PostgreSQL) |
| Медиа-хранилище | Supabase Storage |
| Генерация аватаров | OpenAI GPT Image 2 |
| Хостинг бота | VPS (Ubuntu, systemd) |
| Хостинг веба | Vercel |

## Структура проекта

```
notlove/
├── bot/                    # Telegram-бот (Python)
│   ├── main.py             # Точка входа, polling/webhook
│   ├── handlers.py         # Обработчики команд и FSM
│   ├── avatar.py           # Генерация аватаров через OpenAI API
│   ├── config.py           # Конфигурация, слабости, архетипы
│   ├── db.py               # Работа с Supabase
│   ├── keyboards.py        # Клавиатуры и кнопки
│   ├── texts.py            # Все тексты бота
│   ├── scheduler.py        # Ежедневные напоминания (20:00 МСК)
│   └── requirements.txt    # Зависимости
├── mini-app/               # Telegram Mini App (React)
│   ├── src/
│   │   ├── components/     # PixelAvatar, StreakCalendar, WeaknessCard
│   │   ├── pages/          # HomePage
│   │   └── lib/            # Supabase клиент, Telegram SDK
│   └── vite.config.ts
├── src/                    # Лендинг (Viktor Spaces / React)
│   ├── pages/              # LandingPage, DashboardPage
│   └── components/         # UI-компоненты
├── supabase/
│   └── migrations/         # SQL-миграции
└── convex/                 # Convex (бэкенд для Spaces)
```

## Быстрый старт

### Бот

```bash
cd bot
cp .env.example .env
# Заполни .env реальными ключами

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python main.py  # long-polling для разработки
```

### Мини-аппа

```bash
cd mini-app
npm install
npm run dev
```

### Лендинг

```bash
npm install
npm run dev
```

## Переменные окружения

См. `bot/.env.example` — там все ключи с описанием.

## Архитектура бота

### FSM-состояния

```
/start → Onboarding.waiting_photo → Onboarding.choosing_weaknesses → Onboarding.confirming → Активный вызов
```

### Слабости

| ID | Название | Описание |
|----|----------|----------|
| `sleep` | 🌙 Сон | Ложишься когда придётся, встаёшь никакой |
| `feed` | 📱 Лента | Часы уходят в чужие жизни |
| `porn` | 🔞 18+ | Каждый вечер одно и то же |
| `food` | 🍔 Еда | Топливо из помойки |
| `gym` | 🏋️ Тело | Ни разу не встал ради себя |
| `money` | 💸 Деньги | Тратишь на мусор, копишь на ничего |

### Архетипы

| ID | Название | Комбинация |
|----|----------|-----------|
| `demon` | Ночной Демон | sleep + feed + porn |
| `boss` | Жирный Босс | food + gym |
| `empty` | Пустой Качок | gym + ≤2 слабости |
| `slug` | Сутулый Слизень | feed или sleep |
| `gladiator` | Сырой Гладиатор | всё остальное |

### База данных (Supabase)

**Таблицы:**
- `users` — пользователи (tg_id, username, state, archetype, avatar_url, photo_url)
- `user_weaknesses` — выбранные слабости (tg_id, weakness_id)
- `challenges` — 30-дневные вызовы (tg_id, day, streak, active)
- `checkins` — ежедневные чек-ины (tg_id, challenge_id, day, passed)

### Генерация аватаров

Бот вызывает OpenAI Images API напрямую:
- **С фото:** `POST /v1/images/edits` — трансформация в пиксельного персонажа
- **Без фото:** `POST /v1/images/generations` — генерация дефолтного персонажа
- **Модель:** `gpt-image-2`
- **Стиль:** Lisa: The Painful RPG, CRT/scanlines, тёмное зеркало

### Уведомления

Планировщик в `scheduler.py` — каждый день в 20:00 МСК пингует всех, кто не отчитался.

## Деплой

### Бот (VPS)

```bash
# Копируем файлы
scp bot/*.py user@server:/opt/notlove-bot/

# Рестарт
ssh user@server "systemctl restart notlove-bot"
```

systemd-сервис: `notlove-bot.service`

### Веб (Vercel)

Автодеплой через GitHub. Домен: `notlove-me.vercel.app`

Целевой домен: `notlove.me` (ещё не подключён)

## Визуал

- Пиксельная эстетика уровня Balatro
- CRT/scanlines, тёмное зеркало
- Ограниченная палитра (~20 цветов), тёмные тона
- SNES/GBA era sprite aesthetic

## Аудитория

- РФ, TikTok-трафик
- Весь текст — чистый русский, без англицизмов

## Лицензия

Проприетарный проект.
