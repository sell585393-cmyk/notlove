"""Генерация пиксельного аватара NOTLOVE.ME через OpenAI API.

Прямая генерация — бот вызывает OpenAI Images API напрямую.
"""

from __future__ import annotations

import base64
import io
import logging

import httpx

from config import WEAKNESSES

logger = logging.getLogger(__name__)

OPENAI_API_KEY = ""  # Заполняется из .env через config

GENERATION_PROMPT = """Transform this person's photo into a pixel art character in the style of Lisa: The Painful RPG.

Adapt to the person's ACTUAL appearance: hair color, hair style, skin tone, body build.

Character details:
- Standing in 3/4 side view, slightly slouched, sad/tired posture
- Wearing dark, muted clothing (hoodie or jacket)
- Arms hanging at sides, defeated body language
- One visible eye with white sclera and dark pupil

Background:
- Dark red/brown brick wall behind
- Gray cobblestone floor under feet
- Moody, gritty atmosphere

{weakness_context}

Style:
- Classic pixel art, each pixel clearly visible, NO anti-aliasing
- Limited color palette (~20 colors), dark muted tones
- Character about 60-80 pixels tall (scaled up)
- CRT scanline overlay effect and dark vignette
- SNES/GBA era RPG sprite aesthetic
- DO NOT add any text or labels"""

NO_PHOTO_PROMPT = """Create a pixel art character in the style of Lisa: The Painful RPG.

Character:
- Young person with dark messy hair, pale skin
- 3/4 side view, slouched, sad/tired expression
- Dark oversized hoodie, olive pants, dark shoes
- Arms hanging at sides, defeated posture

Background:
- Dark red/brown brick wall
- Gray cobblestone floor
- Moody, gritty atmosphere

{weakness_context}

Style:
- Classic pixel art, visible pixels, NO anti-aliasing
- ~20 colors, dark muted tones
- CRT scanlines and vignette
- SNES/GBA era sprite aesthetic
- NO text or labels"""


def _init_api_key():
    """Загрузить ключ из окружения."""
    import os
    global OPENAI_API_KEY
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def _build_weakness_context(weaknesses: list[str]) -> str:
    if not weaknesses:
        return ""
    labels = ", ".join(weaknesses)
    return (
        f"Mood context: This person struggles with: {labels}. "
        "Reflect this in body language — more defeated posture, "
        "darker environment, subtle visual hints of their struggles."
    )


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


async def generate_avatar(
    photo_bytes: bytes | None,
    weakness_ids: list[str],
) -> bytes | None:
    """Сгенерировать пиксельный аватар через OpenAI Images API.

    Args:
        photo_bytes: Фото пользователя (или None если пропустил).
        weakness_ids: Список ID слабостей (ключи из WEAKNESSES).

    Returns:
        PNG байты сгенерированного аватара или None при ошибке.
    """
    _init_api_key()
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY не задан")
        return None

    weakness_labels = [
        WEAKNESSES[w]["label"] for w in weakness_ids if w in WEAKNESSES
    ]
    weakness_ctx = _build_weakness_context(weakness_labels)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            if photo_bytes:
                # Генерация с фото — используем images/edits
                prompt = GENERATION_PROMPT.format(weakness_context=weakness_ctx)

                # Подготовим multipart
                files = {
                    "image": ("photo.jpg", photo_bytes, "image/jpeg"),
                }
                data = {
                    "model": "gpt-image-2",
                    "prompt": prompt,
                    "size": "1024x1536",  # 2:3 портрет
                    "quality": "medium",
                }

                resp = await client.post(
                    "https://api.openai.com/v1/images/edits",
                    headers=headers,
                    files=files,
                    data=data,
                )
            else:
                # Без фото — используем images/generations
                prompt = NO_PHOTO_PROMPT.format(weakness_context=weakness_ctx)

                resp = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json={
                        "model": "gpt-image-2",
                        "prompt": prompt,
                        "size": "1024x1536",
                        "quality": "medium",
                    },
                )

            if resp.status_code != 200:
                logger.error(f"OpenAI API error: {resp.status_code} {resp.text}")
                return None

            result = resp.json()
            # gpt-image-2 returns base64 by default
            b64_data = result["data"][0].get("b64_json")
            if b64_data:
                return base64.b64decode(b64_data)

            # fallback: URL
            url = result["data"][0].get("url")
            if url:
                img_resp = await client.get(url)
                if img_resp.status_code == 200:
                    return img_resp.content

            logger.error("No image data in response")
            return None

    except Exception as e:
        logger.error(f"Ошибка генерации аватара: {e}")
        return None
