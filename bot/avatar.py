"""Генерация пиксельного аватара из фото.

На MVP-этапе: берём фото, пикселизируем его (nearest-neighbor downscale → upscale),
накладываем CRT/scanline эффект и рамку в стиле NOTLOVE.
Позже можно подключить AI-генерацию настоящего pixel-art персонажа.
"""

from __future__ import annotations

import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# Палитра NOTLOVE
BG_COLOR = (5, 6, 8)
ACID = (185, 242, 42)
RED = (230, 64, 54)
PANEL = (25, 28, 34)
INK = (238, 241, 232)
MUTED = (139, 151, 143)


def pixelate(img: Image.Image, pixel_size: int = 8) -> Image.Image:
    """Пикселизация изображения через nearest-neighbor."""
    small = img.resize(
        (img.width // pixel_size, img.height // pixel_size),
        resample=Image.Resampling.NEAREST,
    )
    return small.resize(img.size, resample=Image.Resampling.NEAREST)


def add_scanlines(img: Image.Image, opacity: int = 30, spacing: int = 3) -> Image.Image:
    """Накладываем горизонтальные CRT-сканлайны."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, img.height, spacing):
        draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, opacity))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay)


def add_frame(img: Image.Image, archetype: str = "", day: int = 0) -> Image.Image:
    """Рамка в стиле NOTLOVE с архетипом и днём."""
    border = 20
    w, h = img.size
    canvas = Image.new("RGB", (w + border * 2, h + border * 2 + 60), BG_COLOR)

    # Вставляем аватар
    if img.mode == "RGBA":
        canvas.paste(img.convert("RGB"), (border, border))
    else:
        canvas.paste(img, (border, border))

    draw = ImageDraw.Draw(canvas)

    # Рамка
    draw.rectangle(
        [border - 2, border - 2, border + w + 1, border + h + 1],
        outline=ACID, width=2,
    )

    # Текст внизу
    text_y = border + h + 10
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
    except (OSError, IOError):
        font = ImageFont.load_default()

    if archetype:
        draw.text((border, text_y), archetype.upper(), fill=ACID, font=font)
    if day > 0:
        day_text = f"ДЕНЬ {day}/30"
        draw.text((border, text_y + 20), day_text, fill=MUTED, font=font)

    return canvas


def determine_archetype(weaknesses: list[str]) -> str:
    """Определить архетип по слабостям."""
    w = set(weaknesses)

    if {"sleep", "feed", "porn"} & w == {"sleep", "feed", "porn"}:
        return "Ночной Демон"
    if "gym" in w and "food" in w:
        return "Жирный Босс"
    if "gym" in w and len(w) <= 2:
        return "Пустой Качок"
    if "feed" in w or "sleep" in w:
        return "Сутулый Слизень"
    return "Сырой Гладиатор"


def generate_avatar(
    photo_bytes: bytes,
    weaknesses: list[str] | None = None,
    day: int = 0,
    pixel_size: int = 8,
) -> bytes:
    """Генерирует пиксельный аватар из фото.

    Возвращает PNG в байтах.
    """
    img = Image.open(io.BytesIO(photo_bytes))

    # Обрезаем до квадрата
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side))

    # Ресайз до 512x512
    img = img.resize((512, 512), resample=Image.Resampling.LANCZOS)

    # Пикселизация
    img = pixelate(img, pixel_size)

    # Немного затемняем и добавляем зеленоватый оттенок (тёмное зеркало)
    img = img.convert("RGB")
    pixels = img.load()
    if pixels is not None:
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                # Немного сдвигаем в холодный зеленоватый
                r = int(r * 0.7)
                g = int(g * 0.85)
                b = int(b * 0.75)
                pixels[x, y] = (r, g, b)

    # Сканлайны
    img = add_scanlines(img)

    # Архетип
    archetype = determine_archetype(weaknesses or [])

    # Рамка
    img = add_frame(img, archetype=archetype, day=day)

    # В байты
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", quality=95)
    return buf.getvalue()
