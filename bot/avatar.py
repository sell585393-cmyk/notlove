"""Генерация пиксельного аватара NOTLOVE.ME

Бот создаёт запрос (marker в avatar_url), Viktor по крону
генерирует через GPT Image 2 и обновляет URL.
"""

from __future__ import annotations

import asyncio
import logging

from supabase import Client

import db

logger = logging.getLogger(__name__)

# Префикс маркера запроса
PENDING_PREFIX = "pending:"


def request_avatar(
    tg_id: int,
    archetype: str = "slug",
    weaknesses: list[str] | None = None,
) -> None:
    """Создать запрос на генерацию аватара.

    Записывает маркер в avatar_url: 'pending:archetype:w1,w2,w3'
    Viktor-крон подхватит и сгенерирует.
    """
    weakness_str = ",".join(weaknesses or [])
    marker = f"{PENDING_PREFIX}{archetype}:{weakness_str}"
    db.update_user(tg_id, avatar_url=marker)
    logger.info(f"Запрос аватара: tg_id={tg_id}, marker={marker}")


async def poll_avatar(
    tg_id: int,
    timeout: float = 180,
    interval: float = 5,
) -> str | None:
    """Ждать завершения генерации аватара.

    Поллит avatar_url каждые `interval` секунд.
    Возвращает URL готового аватара или None при таймауте.
    """
    elapsed = 0.0
    while elapsed < timeout:
        user = db.get_user(tg_id)
        if user and user.get("avatar_url"):
            url = user["avatar_url"]
            if not url.startswith(PENDING_PREFIX):
                logger.info(f"Аватар готов: tg_id={tg_id}, url={url}")
                return url
        await asyncio.sleep(interval)
        elapsed += interval

    logger.warning(f"Таймаут генерации аватара: tg_id={tg_id}")
    return None


async def download_avatar(avatar_url: str) -> bytes | None:
    """Скачать сгенерированный аватар по URL."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(avatar_url)
            if resp.status_code == 200:
                return resp.content
    except Exception as e:
        logger.error(f"Не удалось скачать аватар: {e}")
    return None


def is_avatar_pending(tg_id: int) -> bool:
    """Проверить, ждёт ли аватар генерации."""
    user = db.get_user(tg_id)
    if user and user.get("avatar_url"):
        return user["avatar_url"].startswith(PENDING_PREFIX)
    return False


# Обратная совместимость
def determine_archetype(weaknesses: list[str]) -> str:
    """Определить архетип по слабостям."""
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
