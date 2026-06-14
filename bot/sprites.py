"""Шаблонная система пиксельных спрайтов NOTLOVE.ME

Модульный персонаж из 2D-массивов пикселей.
Вариации по архетипу, слабостям и дню вызова.
Рендер через Pillow — без внешних API.
"""

from __future__ import annotations
from PIL import Image
import io
import random

# ─── Палитра ──────────────────────────────────────────────────────

P = {
    "BG":      (14, 14, 18),
    "BRICK1":  (82, 38, 32),
    "BRICK2":  (62, 28, 24),
    "BRICK3":  (48, 22, 18),
    "BRICKH":  (95, 50, 42),
    "MORTAR":  (32, 22, 20),
    "FLOOR1":  (50, 47, 44),
    "FLOOR2":  (38, 36, 34),
    "FLOOR3":  (58, 54, 50),
    "FLOORH":  (65, 60, 56),

    "SKIN":    (195, 160, 130),
    "SKIN_S":  (155, 120, 95),
    "SKIN_H":  (218, 190, 160),
    "SKIN_D":  (130, 95, 75),

    "HAIR":    (38, 32, 28),
    "HAIR_H":  (58, 48, 42),
    "HAIR_D":  (22, 18, 15),

    "EYE_W":   (210, 205, 200),
    "EYE_P":   (18, 15, 12),
    "EYE_BAG": (145, 112, 95),

    "HOOD":    (42, 58, 38),
    "HOOD_S":  (30, 42, 27),
    "HOOD_H":  (58, 75, 52),
    "HOOD_D":  (22, 32, 20),

    "PANTS":   (88, 75, 58),
    "PANTS_S": (68, 58, 45),
    "PANTS_H": (105, 90, 70),
    "PANTS_D": (52, 44, 35),

    "BOOTS":   (32, 27, 24),
    "BOOTS_H": (48, 40, 35),
    "BOOTS_D": (20, 16, 14),

    "SHADOW":  (8, 8, 10),
    "OUTLINE": (18, 15, 14),
    "NONE":    None,
}


# ─── Шаблон персонажа (боковая поза, сутулый, день 0) ─────────
# 32 wide x 52 tall — крупный, детализированный
# Поза: полубоком, голова наклонена, плечи опущены

CHAR_TEMPLATE = [
    # Волосы верх (растрёпанные)                                   y=0
    "........OHHHddO..............",  # 0
    ".......OHHHHHdHO.............",  # 1
    "......OHHhHHHHHHO............",  # 2
    ".....OHHhHHHHHHHdO...........",  # 3
    ".....OHHHhHHHHHHHO...........",  # 4
    "....OHHHHhHHHHHHHdO..........",  # 5

    # Лицо — вид полубоком
    "....OHHHSSSSSSHHdO...........",  # 6
    "....OHSSSSSSSSSHO............",  # 7
    "....OSSsWeWSSSSSO............",  # 8  — глаза
    "....OSSSSsSSSSSsO............",  # 9  — нос тень
    "....OSSSSsSSSsSsO............",  # 10
    ".....OSSSSmmSSSO.............",  # 11 — рот
    ".....OSSSSSSsSO..............",  # 12
    "......ObSSSSSO...............",  # 13 — подбородок, мешки
    "......OOSSSOOO...............",  # 14 — шея

    # Худи — верх, капюшон за шеей
    ".....OGGGGGGGGO..............",  # 15
    "....OGGGGGGGGggO.............",  # 16
    "...OGGGhGGGGGggGO............",  # 17
    "..OGGGGhGGGGGggGGO...........",  # 18
    "..OGGGGhGGGGGgGGGO...........",  # 19
    ".OGGGGGhGGGGGGGGGGO..........",  # 20
    ".OGGGGGGGGGGGGGGGdO..........",  # 21

    # Худи — тело (руки вдоль тела)
    ".OGGdGGGGGGGGGGGdGO..........",  # 22
    ".OGGdGGGGGGGGGGGGdO..........",  # 23
    ".OGddGGGGGGGGGGGGdO..........",  # 24
    "..OdGGGGGGGGGGGGdO...........",  # 25
    "..OGGGGGGGGGGGGGdO...........",  # 26
    "..OGGGGGGGGGGGGGdO...........",  # 27
    "...OGGGGGGGGGGGdO............",  # 28
    "...OGGGGGGGGGGGdO............",  # 29

    # Карманы / низ худи
    "...OGGGdddGGGGdO.............",  # 30
    "...OGGGdddGGGGdO.............",  # 31
    "....OGGGGGGGGdO..............",  # 32
    "....OGGGGGGGGdO..............",  # 33

    # Штаны
    "....OPPPPPPPPpO..............",  # 34
    "....OPPPPPPPPpO..............",  # 35
    "....OPPPpPPPPpO..............",  # 36
    "....OPPPpPPPPpO..............",  # 37
    "....OPPPpPPpPpO..............",  # 38
    "...OPPPPpPPpPPpO.............",  # 39
    "...OPPPPpOOPpPPO.............",  # 40
    "...OPPPpO..OpPPO.............",  # 41
    "...OPPPpO..OpPPO.............",  # 42

    # Ботинки
    "...OBBBbO..ObBBO.............",  # 43
    "..OBBBBbO..OBBBbO............",  # 44
    "..OBBBBbO..OBBBbO............",  # 45
    "..OBBBBhO..OBBBhO............",  # 46
    "..OOOOOOO..OOOOOO............",  # 47
]


LEGEND = {
    ".": "NONE",
    "O": "OUTLINE",
    "H": "HAIR",
    "h": "HAIR_H",
    "d": "HAIR_D",
    "S": "SKIN",
    "s": "SKIN_S",
    "W": "EYE_W",
    "e": "EYE_P",
    "b": "EYE_BAG",
    "m": "SKIN_D",      # рот
    "G": "HOOD",
    "g": "HOOD_S",
    "P": "PANTS",
    "p": "PANTS_S",
    "B": "BOOTS",
    # reuse
}

# Переопределим legend чтобы не путать BOOTS_H
LEGEND_FULL = dict(LEGEND)
# В ботинках: b = BOOTS (основной), h в контексте ботинок = BOOTS_H
# Нужно контекстное переопределение — проще сделать два прохода


def _parse_template(template: list[str]) -> list[list[str]]:
    """Парсинг шаблона в массив ключей палитры."""
    rows = []
    for line in template:
        row = []
        for ch in line:
            row.append(LEGEND.get(ch, "NONE"))
        rows.append(row)
    return rows


# ─── Фон ──────────────────────────────────────────────────────────

def _make_background(w: int, h: int, seed: int = 42) -> list[list[str]]:
    rng = random.Random(seed)
    grid = [["BG"] * w for _ in range(h)]

    wall_h = int(h * 0.73)
    brick_h, brick_w = 6, 14

    for y in range(wall_h):
        row_in = y % brick_h
        offset = 0 if (y // brick_h) % 2 == 0 else brick_w // 2

        for x in range(w):
            bx = (x + offset) % brick_w
            if row_in == 0:
                grid[y][x] = "MORTAR"
            elif bx == 0:
                grid[y][x] = "MORTAR"
            else:
                # Вариация цвета кирпича
                v = rng.random()
                if v < 0.15:
                    grid[y][x] = "BRICKH"
                elif v < 0.5:
                    grid[y][x] = "BRICK1"
                elif v < 0.8:
                    grid[y][x] = "BRICK2"
                else:
                    grid[y][x] = "BRICK3"

    # Пол
    for y in range(wall_h, h):
        for x in range(w):
            v = rng.random()
            if v < 0.1:
                grid[y][x] = "FLOORH"
            elif v < 0.45:
                grid[y][x] = "FLOOR1"
            elif v < 0.75:
                grid[y][x] = "FLOOR3"
            else:
                grid[y][x] = "FLOOR2"

    return grid


# ─── Цветовые вариации ────────────────────────────────────────────

def _archetype_palette(archetype: str, day: int) -> dict:
    """Модифицированная палитра по архетипу и дню."""
    mods = {}

    if archetype == "demon":
        mods.update({
            "HOOD": (55, 28, 38), "HOOD_S": (40, 20, 28), "HOOD_D": (28, 14, 20),
            "EYE_P": (170, 35, 25),
        })
    elif archetype == "boss":
        mods.update({
            "HOOD": (60, 55, 42), "HOOD_S": (45, 40, 30),
            "PANTS": (75, 68, 58),
        })
    elif archetype == "empty":
        mods.update({
            "HOOD": (38, 38, 55), "HOOD_S": (28, 28, 42),
        })
    elif archetype == "gladiator":
        mods.update({
            "HOOD": (60, 42, 32), "HOOD_S": (45, 30, 22),
        })

    # Эволюция по дням
    if day >= 7:
        # Немного светлее
        for k in ("HOOD", "HOOD_S", "PANTS"):
            if k in mods:
                r, g, b = mods[k]
            else:
                r, g, b = P[k]
            mods[k] = (min(r + 10, 255), min(g + 10, 255), min(b + 8, 255))
    if day >= 14:
        mods["SKIN"] = (205, 170, 140)
        mods["SKIN_H"] = (225, 195, 168)
    if day >= 21:
        for k in ("HOOD", "HOOD_S"):
            if k in mods:
                r, g, b = mods[k]
            else:
                r, g, b = P[k]
            mods[k] = (min(r + 20, 255), min(g + 20, 255), min(b + 15, 255))

    return mods


# ─── Главная сборка ───────────────────────────────────────────────

def build_sprite(
    archetype: str = "slug",
    weaknesses: list[str] | None = None,
    day: int = 0,
    canvas_w: int = 64,
    canvas_h: int = 96,
) -> list[list[tuple[int, int, int]]]:
    """Собрать спрайт: фон + персонаж."""
    bg = _make_background(canvas_w, canvas_h)
    char_grid = _parse_template(CHAR_TEMPLATE)

    # Позиция персонажа (центр-лево, на полу)
    char_w = max(len(r) for r in char_grid)
    char_h = len(char_grid)
    char_x = (canvas_w - char_w) // 2 - 2
    char_y = canvas_h - char_h - int(canvas_h * 0.27) + 8

    # Палитра с модификациями
    palette = dict(P)
    palette.update(_archetype_palette(archetype, day))

    def resolve(key: str) -> tuple[int, int, int]:
        c = palette.get(key)
        return c if c else (14, 14, 18)

    # Собираем
    result = []
    for y in range(canvas_h):
        row = []
        for x in range(canvas_w):
            cy = y - char_y
            cx = x - char_x
            drawn = False
            if 0 <= cy < char_h and 0 <= cx < len(char_grid[cy]):
                key = char_grid[cy][cx]
                if key != "NONE":
                    # Контекстное переопределение для ботинок
                    if cy >= 43 and key == "HAIR_H":
                        key = "BOOTS_H"
                    if cy >= 43 and key == "EYE_BAG":
                        key = "BOOTS"
                    row.append(resolve(key))
                    drawn = True

            if not drawn:
                row.append(resolve(bg[y][x]))
        result.append(row)

    # Тень под ногами
    foot_y = char_y + char_h
    for dy in range(4):
        y = foot_y + dy
        if 0 <= y < canvas_h:
            darken = 0.55 + dy * 0.1
            for dx in range(-3, char_w + 3):
                x = char_x + dx
                if 0 <= x < canvas_w:
                    r, g, b = result[y][x]
                    result[y][x] = (int(r * darken), int(g * darken), int(b * darken))

    return result


def render_png(
    sprite: list[list[tuple]],
    scale: int = 8,
    scanlines: bool = True,
    vignette: bool = True,
) -> bytes:
    """Рендер спрайта в PNG с эффектами."""
    h = len(sprite)
    w = len(sprite[0]) if sprite else 0
    iw, ih = w * scale, h * scale
    img = Image.new("RGB", (iw, ih), (14, 14, 18))

    # Рисуем пиксели
    for y, row in enumerate(sprite):
        for x, color in enumerate(row):
            if color:
                px, py = x * scale, y * scale
                for sy in range(scale):
                    for sx in range(scale):
                        img.putpixel((px + sx, py + sy), color)

    # Scanlines (CRT эффект)
    if scanlines:
        for y in range(ih):
            if y % 3 == 0:
                for x in range(iw):
                    r, g, b = img.getpixel((x, y))
                    img.putpixel((x, y), (int(r * 0.8), int(g * 0.8), int(b * 0.8)))

    # Виньетка (затемнение краёв)
    if vignette:
        cx, cy = iw / 2, ih / 2
        max_d = (cx ** 2 + cy ** 2) ** 0.5
        for y in range(0, ih, scale):
            for x in range(0, iw, scale):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                factor = max(0.5, 1.0 - (d / max_d) * 0.6)
                r, g, b = img.getpixel((x, y))
                nr, ng, nb = int(r * factor), int(g * factor), int(b * factor)
                for sy in range(scale):
                    for sx in range(scale):
                        if x + sx < iw and y + sy < ih:
                            or_, og, ob = img.getpixel((x + sx, y + sy))
                            f = factor
                            img.putpixel((x + sx, y + sy), (int(or_ * f), int(og * f), int(ob * f)))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
