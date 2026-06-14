"""Обработчики команд и сообщений бота NOTLOVE.ME"""

from __future__ import annotations

import logging
from typing import Any

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType, BufferedInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import WEAKNESSES, ARCHETYPES
from keyboards import (
    main_menu_kb,
    mini_app_kb,
    weaknesses_kb,
    checkin_result_kb,
    confirm_start_kb,
    photo_skip_kb,
)
from texts import (
    WELCOME, PHOTO_RECEIVED, PHOTO_SKIP,
    WEAKNESSES_CHOSEN, CHALLENGE_STARTED,
    DAILY_CHECKIN, CHECKIN_ALL_HELD, CHECKIN_HAD_FAIL,
    ALREADY_CHECKED_IN, CHALLENGE_COMPLETE, PROGRESS,
    NO_ACTIVE_CHALLENGE, NOT_YET,
    progress_bar, get_motivation,
)
import db
from avatar import generate_avatar, determine_archetype

logger = logging.getLogger(__name__)
router = Router()


# ─── FSM состояния ───────────────────────────────────────────────

class Onboarding(StatesGroup):
    waiting_photo = State()
    choosing_weaknesses = State()
    confirming = State()


class CheckinFlow(StatesGroup):
    answering = State()


# ─── /start ──────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    user = db.get_user(tg_id)

    if user is None:
        db.create_user(
            tg_id=tg_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

    # Проверяем, есть ли активный вызов
    challenge = db.get_active_challenge(tg_id)
    if challenge:
        await message.answer(
            f"У тебя уже идёт вызов. День {challenge['day']} из 30.\n"
            "Напиши «Чек-ин» или нажми кнопку.",
            reply_markup=main_menu_kb(),
        )
        return

    await message.answer(
        WELCOME,
        parse_mode="Markdown",
        reply_markup=photo_skip_kb(),
    )
    await state.set_state(Onboarding.waiting_photo)


# ─── Получение фото ─────────────────────────────────────────────

@router.message(Onboarding.waiting_photo, F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    tg_id = message.from_user.id
    photo = message.photo[-1]  # Самое большое разрешение

    # Скачиваем фото
    file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file.file_path)
    photo_data = photo_bytes.read()

    # Сохраняем оригинал в Supabase
    try:
        photo_url = db.upload_photo_to_storage(tg_id, photo_data, "original.jpg")
        db.update_user(tg_id, photo_url=photo_url)
    except Exception as e:
        logger.error(f"Не удалось загрузить фото: {e}")

    # Сохраняем фото в FSM для генерации аватара позже
    await state.update_data(photo_bytes=photo_data)

    await message.answer(
        PHOTO_RECEIVED,
        parse_mode="Markdown",
        reply_markup=weaknesses_kb(),
    )
    await state.set_state(Onboarding.choosing_weaknesses)
    await state.update_data(selected_weaknesses=set())


@router.callback_query(Onboarding.waiting_photo, F.data == "skip_photo")
async def skip_photo(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text(
        PHOTO_SKIP,
        parse_mode="Markdown",
    )
    await callback.message.answer(
        "Выбери слабости:",
        reply_markup=weaknesses_kb(),
    )
    await state.set_state(Onboarding.choosing_weaknesses)
    await state.update_data(selected_weaknesses=set(), photo_bytes=None)


# ─── Выбор слабостей ─────────────────────────────────────────────

@router.callback_query(Onboarding.choosing_weaknesses, F.data.startswith("w:"))
async def handle_weakness_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected: set[str] = data.get("selected_weaknesses", set())
    action = callback.data.split(":")[1]

    if action == "done":
        if not selected:
            await callback.answer("Выбери хотя бы одну слабость")
            return

        tg_id = callback.from_user.id
        weakness_list = list(selected)

        # Сохраняем
        db.set_weaknesses(tg_id, weakness_list)

        # Определяем архетип
        archetype_id = _get_archetype_id(weakness_list)
        archetype_data = ARCHETYPES.get(archetype_id, ARCHETYPES["slug"])
        db.update_user(tg_id, archetype=archetype_id, state="ready")

        # Формируем текст
        wlist = "\n".join(
            f"• {WEAKNESSES[w]['emoji']} {WEAKNESSES[w]['label']} — {WEAKNESSES[w]['desc']}"
            for w in weakness_list
        )

        await callback.message.edit_text(
            WEAKNESSES_CHOSEN.format(
                weakness_list=wlist,
                archetype=archetype_data["label"],
                archetype_desc=archetype_data["desc"],
            ),
            parse_mode="Markdown",
            reply_markup=confirm_start_kb(),
        )

        # Генерируем аватар через OpenAI API
        photo_bytes = data.get("photo_bytes")
        try:
            status_msg = await callback.message.answer(
                "⏳ Рисую твоего двойника..."
            )

            avatar_bytes = await generate_avatar(
                photo_bytes=photo_bytes,
                weakness_ids=weakness_list,
            )

            if avatar_bytes:
                # Загружаем в Supabase Storage
                try:
                    avatar_url = db.upload_photo_to_storage(
                        tg_id, avatar_bytes, "avatar.png"
                    )
                    db.save_avatar_url(tg_id, avatar_url)
                except Exception as e:
                    logger.error(f"Ошибка загрузки аватара в storage: {e}")

                await callback.message.answer_photo(
                    BufferedInputFile(avatar_bytes, filename="avatar.png"),
                    caption="Вот он — твой пиксельный двойник. Диагноз, не портрет.",
                )

                # Удаляем сообщение "Рисую..."
                try:
                    await status_msg.delete()
                except Exception:
                    pass
            else:
                await status_msg.edit_text(
                    "Не удалось создать аватар. Попробуй позже через «👤 Мой персонаж»."
                )
        except Exception as e:
            logger.error(f"Ошибка генерации аватара: {e}")

        await state.set_state(Onboarding.confirming)
        return

    # Переключаем слабость
    if action in selected:
        selected.discard(action)
    elif len(selected) < 3:
        selected.add(action)
    else:
        await callback.answer("Максимум 3 слабости")
        return

    await state.update_data(selected_weaknesses=selected)
    await callback.message.edit_reply_markup(reply_markup=weaknesses_kb(selected))
    await callback.answer()


# ─── Подтверждение старта ────────────────────────────────────────

@router.callback_query(Onboarding.confirming, F.data == "start_challenge")
async def start_challenge_handler(callback: CallbackQuery, state: FSMContext) -> None:
    tg_id = callback.from_user.id

    # Запускаем вызов
    challenge = db.start_challenge(tg_id)
    db.update_user(tg_id, state="active")

    await callback.message.edit_text(
        CHALLENGE_STARTED,
        parse_mode="Markdown",
    )
    await callback.message.answer(
        "Используй кнопки внизу для навигации.",
        reply_markup=main_menu_kb(),
    )
    await state.clear()


@router.callback_query(Onboarding.confirming, F.data == "not_yet")
async def not_yet_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(NOT_YET, parse_mode="Markdown")
    await state.clear()


# ─── Чек-ин ──────────────────────────────────────────────────────

@router.message(F.text.in_({"✅ Чек-ин", "/checkin"}))
async def checkin_start(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    challenge = db.get_active_challenge(tg_id)

    if not challenge:
        await message.answer(NO_ACTIVE_CHALLENGE, parse_mode="Markdown")
        return

    if db.has_checkin_today(tg_id, challenge["id"]):
        await message.answer(ALREADY_CHECKED_IN)
        return

    weaknesses = db.get_weaknesses(tg_id)

    await message.answer(
        DAILY_CHECKIN.format(day=challenge["day"], streak=challenge["streak"]),
        parse_mode="Markdown",
        reply_markup=checkin_result_kb(weaknesses, {}),
    )
    await state.set_state(CheckinFlow.answering)
    await state.update_data(checkin_results={}, challenge_id=challenge["id"], day=challenge["day"])


@router.callback_query(CheckinFlow.answering, F.data.startswith("ci:"))
async def handle_checkin_answer(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split(":")
    action = parts[1]

    data = await state.get_data()
    results: dict[str, bool] = data.get("checkin_results", {})
    challenge_id = data["challenge_id"]
    day = data["day"]
    tg_id = callback.from_user.id

    if action == "held":
        wid = parts[2]
        results[wid] = True
    elif action == "fail":
        wid = parts[2]
        results[wid] = False
    elif action == "toggle":
        wid = parts[2]
        results[wid] = not results.get(wid, True)
    elif action == "submit":
        # Все ответы должны быть заполнены
        weaknesses = db.get_weaknesses(tg_id)
        if not all(w in results for w in weaknesses):
            await callback.answer("Ответь по каждой слабости")
            return

        # Записываем чек-ин
        all_held = all(results.values())
        held_list = [w for w, v in results.items() if v]
        db.add_checkin(tg_id, challenge_id, day, all_held, held_list)

        # Обновляем вызов
        challenge = db.get_active_challenge(tg_id)
        if challenge:
            new_streak = (challenge["streak"] + 1) if all_held else 0
            new_day = challenge["day"] + 1
            total_checkins = challenge["total_checkins"] + 1
            total_fails = challenge["total_fails"] + (0 if all_held else 1)

            if new_day > 30:
                # Вызов завершён!
                db.update_challenge(challenge["id"],
                    active=False,
                    streak=new_streak,
                    total_checkins=total_checkins,
                    total_fails=total_fails,
                )

                best_streak = max(new_streak, challenge.get("best_streak", 0))
                if total_fails == 0:
                    final = "Ни одного срыва. Ты — другой человек."
                elif total_fails <= 3:
                    final = "Почти без срывов. Ты доказал, что можешь."
                else:
                    final = "Были срывы. Но ты не бросил. Это главное."

                await callback.message.edit_text(
                    CHALLENGE_COMPLETE.format(
                        total_checkins=total_checkins,
                        total_fails=total_fails,
                        best_streak=best_streak,
                        final_message=final,
                    ),
                    parse_mode="Markdown",
                )
                await state.clear()
                return

            db.update_challenge(challenge["id"],
                day=new_day,
                streak=new_streak,
                total_checkins=total_checkins,
                total_fails=total_fails,
            )

            days_left = 30 - day

            if all_held:
                text = CHECKIN_ALL_HELD.format(
                    streak=new_streak,
                    motivation=get_motivation(new_streak),
                    days_left=days_left,
                )
            else:
                failed = [WEAKNESSES[w]["label"] for w, v in results.items() if not v]
                fail_text = "Сорвался: " + ", ".join(failed)
                text = CHECKIN_HAD_FAIL.format(
                    fail_text=fail_text,
                    days_left=days_left,
                )

            await callback.message.edit_text(text, parse_mode="Markdown")

        await state.clear()
        return

    await state.update_data(checkin_results=results)
    weaknesses = db.get_weaknesses(tg_id)
    await callback.message.edit_reply_markup(
        reply_markup=checkin_result_kb(weaknesses, results),
    )
    await callback.answer()


# ─── Прогресс ────────────────────────────────────────────────────

@router.message(F.text.in_({"📊 Мой прогресс", "/progress"}))
async def show_progress(message: Message) -> None:
    tg_id = message.from_user.id
    challenge = db.get_active_challenge(tg_id)

    if not challenge:
        await message.answer(NO_ACTIVE_CHALLENGE, parse_mode="Markdown")
        return

    day = challenge["day"]
    streak = challenge["streak"]
    bar = progress_bar(day)

    if streak >= 7:
        status = "🔥 Ты в ударе. Не останавливайся."
    elif streak >= 3:
        status = "💪 Набираешь обороты."
    elif streak == 0:
        status = "⚠️ Стрик сброшен. Начни заново."
    else:
        status = "Каждый день на счету."

    await message.answer(
        PROGRESS.format(
            day=day,
            streak=streak,
            total_checkins=challenge["total_checkins"],
            total_fails=challenge["total_fails"],
            bar=bar,
            status=status,
        ),
        parse_mode="Markdown",
    )


# ─── Мой персонаж ───────────────────────────────────────────────

@router.message(F.text.in_({"👤 Мой персонаж", "/avatar"}))
async def show_avatar(message: Message) -> None:
    tg_id = message.from_user.id
    user = db.get_user(tg_id)

    if not user:
        await message.answer("Напиши /start чтобы начать.")
        return

    avatar_url = user.get("avatar_url")
    if avatar_url and not avatar_url.startswith("pending:") and not avatar_url.startswith("error:"):
        await message.answer_photo(
            avatar_url,
            caption="Твой пиксельный двойник. Он меняется вместе с тобой.",
            reply_markup=mini_app_kb(),
        )
    else:
        await message.answer(
            "У тебя пока нет персонажа. Скинь фото — и я создам твоего двойника.",
        )


# ─── Настройки ───────────────────────────────────────────────────

@router.message(F.text.in_({"⚙️ Настройки", "/settings"}))
async def show_settings(message: Message) -> None:
    tg_id = message.from_user.id
    user = db.get_user(tg_id)
    weaknesses = db.get_weaknesses(tg_id)

    wlist = ", ".join(WEAKNESSES[w]["label"] for w in weaknesses if w in WEAKNESSES)
    archetype = ARCHETYPES.get(user.get("archetype", ""), {}).get("label", "—")

    await message.answer(
        f"⚙️ *Настройки*\n\n"
        f"Архетип: *{archetype}*\n"
        f"Слабости: {wlist or '—'}\n\n"
        f"Чтобы сбросить и начать заново — /reset",
        parse_mode="Markdown",
    )


# ─── Сброс ───────────────────────────────────────────────────────

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    challenge = db.get_active_challenge(tg_id)
    if challenge:
        db.update_challenge(challenge["id"], active=False)
    db.update_user(tg_id, state="new", archetype=None, avatar_url=None)
    await state.clear()
    await message.answer(
        "Всё сброшено. Напиши /start чтобы начать заново.",
    )


# ─── Помощник ────────────────────────────────────────────────────

def _get_archetype_id(weaknesses: list[str]) -> str:
    """Определить ID архетипа по слабостям."""
    w = set(weaknesses)
    if {"sleep", "feed", "porn"} <= w:
        return "demon"
    if "food" in w and "gym" in w:
        return "boss"
    if "gym" in w and len(w) <= 2:
        return "empty"
    if "feed" in w or "sleep" in w:
        return "slug"
    return "gladiator"
