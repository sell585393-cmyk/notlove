"""Ежедневные напоминания и пинки.

Запускается отдельным планировщиком: каждый день в 20:00 МСК
проходит по всем активным вызовам и отправляет напоминание,
если пользователь ещё не отчитался.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from aiogram import Bot

import db

logger = logging.getLogger(__name__)

MSK = timezone(timedelta(hours=3))


REMINDER_TEXTS = [
    "Эй. Ты сегодня ещё не отчитался. Не прячься.",
    "День заканчивается. Чек-ин ждёт. Честно — держался или сорвался?",
    "Промолчать — тоже ответ. Но я всё равно спрошу: как сегодня?",
    "Тот, кого ты кормишь, надеется, что ты забудешь. Не забывай.",
    "Один пропущенный день — начало конца стрика. Отчитайся.",
    "Зеркало не выключается. Чек-ин.",
]


async def send_daily_reminders(bot: Bot) -> None:
    """Отправить напоминания всем, кто не отчитался сегодня."""
    # Получаем всех пользователей с активным вызовом
    resp = db.get_db().table("challenges").select("tg_id, id").eq("active", True).execute()

    if not resp.data:
        logger.info("Нет активных вызовов")
        return

    import random
    sent = 0

    for challenge in resp.data:
        tg_id = challenge["tg_id"]
        challenge_id = challenge["id"]

        if db.has_checkin_today(tg_id, challenge_id):
            continue

        text = random.choice(REMINDER_TEXTS)
        try:
            await bot.send_message(tg_id, text)
            sent += 1
        except Exception as e:
            logger.warning(f"Не удалось отправить напоминание {tg_id}: {e}")

        # Небольшая задержка, чтобы не спамить API
        await asyncio.sleep(0.1)

    logger.info(f"Отправлено {sent} напоминаний")
