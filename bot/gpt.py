"""Клиент GPT API (freemodel.dev) для NOTLOVE.ME"""

from __future__ import annotations

import logging
import json
from typing import Any

import aiohttp

from config import GPT_API_KEY, GPT_API_URL

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-5.4-mini"


async def chat(
    messages: list[dict[str, Any]],
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """Отправить запрос в GPT и получить текстовый ответ."""
    if not GPT_API_KEY:
        raise RuntimeError("GPT_API_KEY не задан")

    url = f"{GPT_API_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GPT_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"GPT API error {resp.status}: {text}")
            data = await resp.json()
            return data["choices"][0]["message"]["content"]


async def generate_svg_sprite(
    archetype: str,
    weaknesses: list[str],
    day: int = 0,
    appearance: str | None = None,
) -> str:
    """Сгенерировать SVG пиксельного персонажа через GPT.

    Args:
        archetype: ID архетипа (slug, demon, boss, empty, gladiator)
        weaknesses: список слабостей пользователя
        day: день вызова (0=начало, влияет на позу/настроение)
        appearance: описание внешности (опционально, из фото)

    Returns:
        SVG-код персонажа
    """
    # Эволюция персонажа по дням
    if day == 0:
        mood = "подавленный, сутулый, потухший взгляд, руки висят"
        bg = "тёмная кирпичная стена, грязный пол, тусклый свет"
    elif day <= 7:
        mood = "немного выпрямился, искра в глазах, но ещё напряжён"
        bg = "кирпичная стена, но чуть светлее, трещина в стене"
    elif day <= 14:
        mood = "уверенная стойка, плечи расправлены, лёгкая броня"
        bg = "стена чище, появился свет из окна"
    elif day <= 21:
        mood = "сильная поза, аура вокруг, взгляд вперёд"
        bg = "стена с граффити мотивации, тёплый свет"
    else:
        mood = "воин, полная броня, свечение, поднятый подбородок"
        bg = "рассвет за спиной, чистый фон"

    weakness_labels = ", ".join(weaknesses) if weaknesses else "неизвестны"

    system_prompt = """Ты — пиксель-арт художник. Генерируешь SVG-код персонажей в стиле 32-bit pixel art RPG (уровень детализации как в Celeste, Lisa: The Painful, Undertale).

ПРАВИЛА SVG:
1. Размер: viewBox="0 0 128 192" (персонаж в полный рост)
2. Каждый "пиксель" — это <rect> размером 4x4 или 2x2
3. Используй тёмную палитру: чёрный, тёмно-зелёный, коричневый, бордовый, серый
4. Персонаж должен быть в центре, в полный рост
5. Добавь фон (стена, пол) из таких же пикселей
6. Добавь тени и объём через разные оттенки
7. НЕ используй <text>, <image>, фильтры, градиенты
8. Только <svg>, <rect>, <g> теги
9. Стиль: мрачный, атмосферный, как скриншот из инди-RPG

Верни ТОЛЬКО SVG-код, без пояснений, без markdown блоков. Начинай с <svg и заканчивай </svg>."""

    user_prompt = f"""Создай пиксельного персонажа:

Архетип: {archetype}
Слабости: {weakness_labels}
День вызова: {day} из 30

Настроение/поза: {mood}
Фон: {bg}
{f"Внешность: {appearance}" if appearance else "Внешность: молодой парень, тёмные волосы, худой"}

Нарисуй детализированного персонажа с этими характеристиками. Каждая слабость должна отражаться визуально (например, "сон" — мешки под глазами, "еда" — пустые обёртки на полу)."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await chat(messages, model="gpt-5.4", max_tokens=8192, temperature=0.8)

    # Извлекаем SVG из ответа
    svg = _extract_svg(response)
    if not svg:
        raise ValueError("GPT не вернул валидный SVG")

    return svg


def _extract_svg(text: str) -> str | None:
    """Извлечь SVG-код из текста ответа GPT."""
    # Убираем markdown code blocks если есть
    text = text.strip()
    if text.startswith("```"):
        # Убираем ```svg или ```xml или ``` 
        lines = text.split("\n")
        lines = lines[1:]  # убираем первую строку с ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Ищем <svg ... </svg>
    start = text.find("<svg")
    end = text.rfind("</svg>")
    if start >= 0 and end > start:
        return text[start:end + 6]

    return None
