"""Генерация пиксельного аватара NOTLOVE.ME

Использует шаблонную систему спрайтов (sprites.py).
Опционально обогащает через GPT (описание для mini-app).
"""

from __future__ import annotations

import logging

from sprites import build_sprite, render_png

logger = logging.getLogger(__name__)


async def generate_avatar(
    archetype: str,
    weaknesses: list[str],
    day: int = 0,
    appearance: str | None = None,
) -> tuple[bytes, dict]:
    """Сгенерировать аватар.

    Returns:
        (png_bytes, metadata)
    """
    # Собираем спрайт
    sprite = build_sprite(
        archetype=archetype,
        weaknesses=weaknesses,
        day=day,
    )

    # Рендерим в PNG
    png_bytes = render_png(sprite, scale=8, scanlines=True, vignette=True)
    logger.info(f"Аватар: {len(png_bytes)} байт, архетип={archetype}, день={day}")

    metadata = {
        "archetype": archetype,
        "weaknesses": weaknesses,
        "day": day,
    }

    return png_bytes, metadata


def determine_archetype(weaknesses: list[str]) -> str:
    """Определить архетип по слабостям (обратная совместимость)."""
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
