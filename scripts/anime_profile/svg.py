"""Мелкие помощники для сборки SVG: экранирование, перенос строк, лепестки сакуры."""

import random
from xml.sax.saxutils import escape as _escape

from .theme import FONT_STACK, REDUCED_MOTION_CSS

# Лепесток сакуры с характерной «зарубкой» на кончике; основание в (0,0), кончик вверх.
PETAL_PATH = "M0,0 C-7,-5 -8,-13 -3,-18 L0,-15 L3,-18 C8,-13 7,-5 0,0 Z"
# Четырёхлучевая «искорка» ✦
SPARKLE_PATH = "M0,-8 C1,-2 2,-1 8,0 C2,1 1,2 0,8 C-1,2 -2,1 -8,0 C-2,-1 -1,-2 0,-8 Z"


def esc(text) -> str:
    return _escape(str(text), {'"': "&quot;"})


def wrap(text: str, max_chars: int, max_lines: int) -> list[str]:
    """Жадный перенос по словам; лишнее обрезается многоточием."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;:!?… ") + "…"
    return [line if len(line) <= max_chars else line[: max_chars - 1] + "…" for line in lines]


def balanced_wrap(text: str, max_chars: int, max_lines: int) -> list[str]:
    """Как wrap, но строки примерно одной длины — без одинокого слова в конце."""
    count = len(wrap(text, max_chars, max_lines))
    for width in range(-(-len(text) // count), max_chars + 1):
        lines = wrap(text, width, max_lines)
        if len(lines) <= count and not lines[-1].endswith("…"):
            return lines
    return wrap(text, max_chars, max_lines)


def speech_bubble(cx, cy, rx, ry, tx, ty, stroke: str = "#111111", width: float = 3,
                  fill: str = "#fff", spread: float = 0.17) -> str:
    """Облачко-реплика: эллипс с хвостиком, указывающим на точку (tx, ty)."""
    import math
    a0 = math.atan2((ty - cy) / ry, (tx - cx) / rx)
    x1, y1 = cx + rx * math.cos(a0 + spread), cy + ry * math.sin(a0 + spread)
    x2, y2 = cx + rx * math.cos(a0 - spread), cy + ry * math.sin(a0 - spread)
    return (f'<path d="M{x1:.1f},{y1:.1f} A{rx},{ry} 0 1 1 {x2:.1f},{y2:.1f} L{tx},{ty} Z" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"/>')


def truncate(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else text[: max_chars - 1].rstrip() + "…"


def flower(x: float, y: float, scale: float = 1.0, rotate: float = 0.0, fill: str = "url(#petal)") -> str:
    """Цветок сакуры из пяти лепестков."""
    petals = "".join(
        f'<path d="{PETAL_PATH}" transform="rotate({i * 72})" fill="{fill}"/>' for i in range(5)
    )
    center = (
        '<circle r="3.2" fill="#ffe3f1"/>'
        + "".join(
            f'<circle cx="{dx}" cy="{dy}" r="1" fill="#ff5fa2"/>'
            for dx, dy in ((0, -4.5), (4.3, -1.4), (2.6, 3.6), (-2.6, 3.6), (-4.3, -1.4))
        )
    )
    return (
        f'<g transform="translate({x:.1f},{y:.1f}) rotate({rotate:.0f}) scale({scale:.2f})">'
        f"{petals}{center}</g>"
    )


def falling_petals(rng: random.Random, count: int, width: float, height: float,
                   min_scale: float = 0.5, max_scale: float = 1.0, opacity: float = 0.9) -> str:
    """Падающие лепестки: внешняя группа задаёт старт, внутренние — падение, покачивание и вращение."""
    out = []
    for _ in range(count):
        x = rng.uniform(0, width + width * 0.25)
        scale = rng.uniform(min_scale, max_scale)
        fall = rng.uniform(9, 17)
        sway = rng.uniform(2.5, 4.5)
        spin = rng.uniform(3, 7)
        delay = -rng.uniform(0, fall)
        out.append(
            f'<g transform="translate({x:.0f},-24)">'
            f'<g class="fall" style="animation-duration:{fall:.1f}s;animation-delay:{delay:.1f}s">'
            f'<g class="sway" style="animation-duration:{sway:.1f}s;animation-delay:{delay:.1f}s">'
            f'<path class="spin" d="{PETAL_PATH}" fill="url(#petal)" opacity="{opacity}" '
            f'transform="scale({scale:.2f})" style="animation-duration:{spin:.1f}s"/>'
            f"</g></g></g>"
        )
    return "\n".join(out)


def petal_css(fall_distance: float, drift: float = -180) -> str:
    return f"""
    .fall {{ animation: fall linear infinite; }}
    .sway {{ animation: sway ease-in-out infinite alternate; }}
    .spin {{ animation: spin linear infinite; transform-box: fill-box; transform-origin: center; }}
    @keyframes fall {{
      0% {{ transform: translate(0, 0); opacity: 0; }}
      8% {{ opacity: 1; }}
      85% {{ opacity: 1; }}
      100% {{ transform: translate({drift:.0f}px, {fall_distance:.0f}px); opacity: 0; }}
    }}
    @keyframes sway {{ from {{ transform: translateX(-14px); }} to {{ transform: translateX(14px); }} }}
    @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    """


PETAL_GRADIENT = (
    '<linearGradient id="petal" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#ffe3f1"/><stop offset="1" stop-color="#ff8fc7"/>'
    "</linearGradient>"
)


def document(width: int, height: int, title: str, defs: str, css: str, body: str,
             font_css: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">\n'
        f"<title>{esc(title)}</title>\n"
        f"<defs>{defs}</defs>\n"
        f"<style>{font_css}\n"
        f"text {{ font-family: {FONT_STACK}; }}\n"
        f"{css}\n{REDUCED_MOTION_CSS}</style>\n"
        f"{body}\n</svg>\n"
    )
