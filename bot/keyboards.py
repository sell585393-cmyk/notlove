"""Клавиатуры и кнопки для бота NOTLOVE.ME"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)

from config import WEAKNESSES, MINI_APP_URL


# ─── Главное меню ────────────────────────────────────────────────

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 NOTLOVE", web_app=WebAppInfo(url=MINI_APP_URL))],
            [KeyboardButton(text="📊 Мой прогресс"), KeyboardButton(text="✅ Чек-ин")],
            [KeyboardButton(text="👤 Мой персонаж"), KeyboardButton(text="⚙️ Настройки")],
        ],
        resize_keyboard=True,
    )


# ─── Кнопка мини-аппа ───────────────────────────────────────────

def mini_app_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🎮 Открыть NOTLOVE",
                web_app=WebAppInfo(url=MINI_APP_URL),
            )],
        ]
    )


# ─── Выбор слабостей ─────────────────────────────────────────────

def weaknesses_kb(selected: set[str] | None = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора слабостей. Выбранные отмечены ✓."""
    if selected is None:
        selected = set()

    rows: list[list[InlineKeyboardButton]] = []
    items = list(WEAKNESSES.items())

    for i in range(0, len(items), 2):
        row = []
        for wid, w in items[i:i + 2]:
            mark = "✓ " if wid in selected else ""
            row.append(InlineKeyboardButton(
                text=f"{mark}{w['emoji']} {w['label']}",
                callback_data=f"w:{wid}",
            ))
        rows.append(row)

    # Кнопка подтверждения (если выбрано хотя бы 1)
    if selected:
        rows.append([InlineKeyboardButton(
            text=f"Готово ({len(selected)} выбрано)",
            callback_data="w:done",
        )])

    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── Чек-ин ──────────────────────────────────────────────────────

def checkin_kb(weaknesses: list[str]) -> InlineKeyboardMarkup:
    """Кнопки для дневного чек-ина: держался / сорвался по каждой слабости."""
    rows: list[list[InlineKeyboardButton]] = []

    for wid in weaknesses:
        w = WEAKNESSES.get(wid)
        if not w:
            continue
        rows.append([
            InlineKeyboardButton(text=f"✅ {w['label']} — держался", callback_data=f"ci:held:{wid}"),
            InlineKeyboardButton(text=f"❌ {w['label']} — сорвался", callback_data=f"ci:fail:{wid}"),
        ])

    rows.append([InlineKeyboardButton(text="📨 Отправить чек-ин", callback_data="ci:submit")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def checkin_result_kb(weaknesses: list[str], results: dict[str, bool]) -> InlineKeyboardMarkup:
    """Обновлённая клавиатура с отмеченными результатами."""
    rows: list[list[InlineKeyboardButton]] = []

    for wid in weaknesses:
        w = WEAKNESSES.get(wid)
        if not w:
            continue
        if wid in results:
            status = "✅ держался" if results[wid] else "❌ сорвался"
            rows.append([InlineKeyboardButton(
                text=f"{w['emoji']} {w['label']} — {status}",
                callback_data=f"ci:toggle:{wid}",
            )])
        else:
            rows.append([
                InlineKeyboardButton(text=f"✅ {w['label']} — держался", callback_data=f"ci:held:{wid}"),
                InlineKeyboardButton(text=f"❌ {w['label']} — сорвался", callback_data=f"ci:fail:{wid}"),
            ])

    all_answered = all(wid in results for wid in weaknesses)
    if all_answered:
        rows.append([InlineKeyboardButton(text="📨 Отправить чек-ин", callback_data="ci:submit")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── Подтверждения ───────────────────────────────────────────────

def confirm_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Начать 30 дней", callback_data="start_challenge")],
            [InlineKeyboardButton(text="Пока нет", callback_data="not_yet")],
        ]
    )


def photo_skip_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить фото", callback_data="skip_photo")],
        ]
    )
