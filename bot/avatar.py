"""Генерация пиксельного аватара NOTLOVE.ME

GPT-5.5 vision анализирует фото пользователя и генерирует SVG-спрайт
в стиле Lisa: The Painful. SVG рендерится в PNG с CRT-эффектами.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import math

import httpx

logger = logging.getLogger(__name__)

# Попробуем импортировать необходимые библиотеки
try:
    import cairosvg

    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from config import GPT_API_KEY, GPT_API_URL


SPRITE_PROMPT = """You are a pixel art engine. You receive a photo of a person and create their pixel art avatar.

STYLE: Lisa: The Painful RPG — 32-bit indie pixel art. Dark, gritty, emotional.

SVG SPECS:
- viewBox="0 0 48 64"
- Each visual element = <rect x y width height fill="#hex"/>
- Merge adjacent same-color pixels into wider/taller rects to save tokens
- Use <g fill="#hex"> grouping for efficiency
- Target: 200-400 rects for good detail

CHARACTER (adapt to person in photo):
- Side-facing pose, shoulders hunched forward, head slightly down — defeated body language
- ~20px wide, ~38px tall, positioned at x=14
- Black 1px outline around entire character silhouette
- Hair: match person's hair color and style (messy/spiky look)
- Face: side profile — visible eye (white sclera + dark pupil), small nose, thin frowning mouth
- Skin: match person's skin tone (muted version)
- Clothing: match person's clothing colors (muted/darkened versions), slightly baggy
- Hands: skin color, hanging down limply
- Pants: match or default to olive brown, slightly loose
- Shoes: very dark

BACKGROUND:
- Brick wall: rows of bricks using 2-3 brick colors (#6b3a2a, #7a4a3a, #5a2a1a) with dark mortar (#2a1a0a)
- Stone floor: bottom 10 rows, cobblestone pattern (#5a5a5a, #4a4a4a, #3a3a3a)

{weakness_context}

Output ONLY the SVG code. No markdown, no explanation. Start with <svg, end with </svg>."""


def _build_prompt(weaknesses: list[str] | None = None) -> str:
    """Собрать промпт с контекстом слабостей."""
    weakness_text = ""
    if weaknesses:
        labels = ", ".join(weaknesses)
        weakness_text = (
            f"MOOD CONTEXT: This person struggles with: {labels}. "
            "Reflect this in body language and surroundings — more defeated pose, "
            "darker palette, environmental hints of their struggles."
        )
    return SPRITE_PROMPT.format(weakness_context=weakness_text)


async def generate_avatar(
    photo_bytes: bytes | None = None,
    archetype: str = "slug",
    weaknesses: list[str] | None = None,
    day: int = 0,
) -> tuple[bytes, dict]:
    """Сгенерировать аватар через GPT-5.5 vision.

    Args:
        photo_bytes: JPEG/PNG фото пользователя (опционально)
        archetype: архетип персонажа
        weaknesses: список слабостей
        day: день вызова (для эволюции)

    Returns:
        (png_bytes, metadata)
    """
    prompt = _build_prompt(weaknesses)

    # Собираем сообщение
    content_parts: list[dict] = [{"type": "text", "text": prompt}]

    if photo_bytes:
        b64 = base64.b64encode(photo_bytes).decode()
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            }
        )

    # Стриминг запрос к GPT-5.5
    svg_content = ""
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(10, read=600)
    ) as client:
        async with client.stream(
            "POST",
            f"{GPT_API_URL}/v1/chat/completions",
            headers={"Authorization": f"Bearer {GPT_API_KEY}"},
            json={
                "model": "gpt-5.5",
                "messages": [
                    {"role": "user", "content": content_parts}
                ],
                "max_tokens": 16000,
                "temperature": 0.2,
                "stream": True,
            },
        ) as resp:
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        svg_content += delta["content"]
                except Exception:
                    pass

    # Извлекаем SVG
    if "<svg" not in svg_content:
        raise ValueError("GPT не вернул SVG")

    start = svg_content.index("<svg")
    end = (
        svg_content.index("</svg>") + 6
        if "</svg>" in svg_content
        else len(svg_content)
    )
    svg = svg_content[start:end]
    if not svg.endswith("</svg>"):
        svg += "</svg>"

    # SVG → PNG
    png_bytes = _svg_to_png_with_effects(svg, day=day)

    rect_count = svg.count("<rect")
    logger.info(
        f"Аватар: {len(png_bytes)} байт, {rect_count} ректов, "
        f"архетип={archetype}, день={day}"
    )

    metadata = {
        "archetype": archetype,
        "weaknesses": weaknesses or [],
        "day": day,
        "rect_count": rect_count,
        "svg_len": len(svg),
    }

    return png_bytes, metadata


def _svg_to_png_with_effects(
    svg: str, width: int = 384, height: int = 512, day: int = 0
) -> bytes:
    """Рендерим SVG в PNG с CRT-эффектами."""
    if not HAS_CAIROSVG or not HAS_PIL:
        # Фолбек: просто SVG → PNG без эффектов
        if HAS_CAIROSVG:
            return cairosvg.svg2png(
                bytestring=svg.encode(),
                output_width=width,
                output_height=height,
            )
        raise ImportError("cairosvg не установлен")

    # Рендерим SVG
    raw_png = cairosvg.svg2png(
        bytestring=svg.encode(),
        output_width=width,
        output_height=height,
    )
    img = Image.open(io.BytesIO(raw_png)).convert("RGBA")
    w, h = img.size
    pixels = img.load()

    # Эволюция: с каждой неделей яркость растёт
    brightness_boost = 1.0
    if day >= 7:
        brightness_boost = 1.05
    if day >= 14:
        brightness_boost = 1.1
    if day >= 21:
        brightness_boost = 1.2

    # CRT scanlines
    cx, cy = w / 2, h / 2
    max_dist = math.sqrt(cx**2 + cy**2)

    for y in range(h):
        scanline = 0.6 if y % 3 == 2 else 1.0
        for x in range(w):
            r, g, b, a = pixels[x, y]

            # Scanline
            r, g, b = int(r * scanline), int(g * scanline), int(b * scanline)

            # Vignette
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            vig = 1.0 - 0.4 * (dist / max_dist) ** 1.5
            r, g, b = int(r * vig), int(g * vig), int(b * vig)

            # Эволюция (яркость)
            if brightness_boost > 1.0:
                r = min(255, int(r * brightness_boost))
                g = min(255, int(g * brightness_boost))
                b = min(255, int(b * brightness_boost))

            pixels[x, y] = (r, g, b, a)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


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
