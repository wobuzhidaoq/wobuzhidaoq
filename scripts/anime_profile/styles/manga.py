"""🖤 Манга: чёрно-белая страница с панелями, скринтоном, линиями концентрации и облачками.

Картинки берутся из assets/images (config/profile.json → images) и вклеиваются в панели в ч/б.
Единственный цвет — красная печать-ханко.
"""

import datetime as dt
import math
import random

from .. import status_window
from ..quote import PINNED_CAPTION, attribution, pick
from ..svg import SPARKLE_PATH, balanced_wrap, document, esc, speech_bubble, truncate, wrap

INK = "#111111"
GRAY = "#555555"
SOFT = "#8a8a8a"
RED = "#d7263d"
TITLE_FONT = "Dela Gothic One"
BODY_FONT = "Pangolin"       # комиксный леттеринг с нормальной кириллицей
JP_FONT = "Klee One"         # японские буквы, которых нет в Pangolin

FONT_CLASSES = f"""
.t {{ font-family: '{TITLE_FONT}', 'Hiragino Kaku Gothic StdN', 'Yu Gothic', 'Arial Black', sans-serif; }}
.b {{ font-family: '{BODY_FONT}', '{JP_FONT}', 'Comic Sans MS', 'Hiragino Maru Gothic ProN', sans-serif; }}
"""

DEFS = f"""
<pattern id="dots" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <circle cx="3.5" cy="3.5" r="1.3" fill="{INK}"/></pattern>
<pattern id="dotsBig" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <circle cx="4" cy="4" r="2.3" fill="{INK}"/></pattern>
<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <rect width="2.2" height="6" fill="{INK}"/></pattern>
<radialGradient id="fadeOut" cx=".5" cy=".5" r=".62"><stop offset="0" stop-color="#000"/>
  <stop offset=".5" stop-color="#000"/><stop offset="1" stop-color="#fff"/></radialGradient>
<linearGradient id="fadeDown" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/>
  <stop offset="1" stop-color="#000"/></linearGradient>
<filter id="ink" x="-3%" y="-3%" width="106%" height="106%">
  <feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="4" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="2.4"/></filter>
<filter id="gray"><feColorMatrix type="saturate" values="0"/></filter>
"""

CSS = FONT_CLASSES + """
.flick { animation: flick 1.4s steps(2) infinite; }
@keyframes flick { 50% { opacity: .78; } }
.pop { animation: pop .7s cubic-bezier(.2,1.5,.4,1) both; transform-box: fill-box; transform-origin: center; }
@keyframes pop { from { transform: scale(.2); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.stamp { animation: stamp .45s cubic-bezier(.3,1.6,.5,1) both; transform-box: fill-box; transform-origin: center; }
@keyframes stamp { from { transform: scale(2.6); opacity: 0; } to { transform: scale(1); opacity: .92; } }
.shake { animation: shake 5s infinite; transform-box: fill-box; transform-origin: center; }
@keyframes shake { 0%, 88%, 100% { transform: none; } 90% { transform: translate(-3px, 1px); }
  92% { transform: translate(3px, -1px); } 94% { transform: translate(-2px, 0); } 96% { transform: translate(2px, 1px); } }
.zoom { animation: zoom 14s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }
@keyframes zoom { from { transform: scale(1); } to { transform: scale(1.06); } }
.slide { animation: slide 1s cubic-bezier(.2,.8,.2,1) both; }
@keyframes slide { from { transform: translateX(170px); opacity: 0; } to { transform: none; opacity: 1; } }
.grow { animation: grow 1.4s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: left center; }
@keyframes grow { from { transform: scaleX(0); } }
.growY { animation: growY 1.2s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: center bottom; }
@keyframes growY { from { transform: scaleY(0); } }
.draw { animation: draw 1.2s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: center; }
@keyframes draw { from { transform: scaleX(0); } }
.spin { animation: spin 10s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spin { to { transform: rotate(360deg); } }
.rise { animation: rise 1.2s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
"""


class Text:
    """Собирает все надписи по шрифтам, чтобы встроить только нужные буквы."""

    def __init__(self):
        self.title: list[str] = []
        self.body: list[str] = []

    def t(self, x, y, value, size, fill=INK, anchor="start", extra=""):
        self.title.append(str(value))
        return (f'<text class="t" x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                f'{extra}>{esc(value)}</text>')

    def b(self, x, y, value, size, fill=INK, anchor="start", weight=None, extra=""):
        self.body.append(str(value))
        return (f'<text class="b" x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
                f'text-anchor="{anchor}" {extra}>{esc(value)}</text>')

    def fonts(self, ctx) -> str:
        body = "".join(self.body)
        jp = "".join(c for c in body if ord(c) >= 0x3000)
        return (ctx.fonts.css("".join(self.title), (400,), TITLE_FONT)
                + ctx.fonts.css(body, (400,), BODY_FONT)
                + (ctx.fonts.css(jp, (400,), JP_FONT) if jp else ""))


# ---------------------------------------------------------------------------
# Кирпичики манги
# ---------------------------------------------------------------------------


def _pts(points) -> str:
    return " ".join(f"{x},{y}" for x, y in points)


def panel(pid: str, points, content: str, stroke: float = 5) -> str:
    """Панель манги произвольной формы: белая подложка, содержимое по маске, чернильная рамка."""
    pts = _pts(points)
    return (f'<clipPath id="{pid}"><polygon points="{pts}"/></clipPath>'
            f'<g clip-path="url(#{pid})"><polygon points="{pts}" fill="#fff"/>{content}</g>'
            f'<polygon points="{pts}" fill="none" stroke="{INK}" stroke-width="{stroke}" '
            f'stroke-linejoin="miter" filter="url(#ink)"/>')


def picture(ctx, key: str, x, y, w, h, max_side: int = 640) -> str:
    uri = ctx.images.uri(key, max_side, grayscale=True)
    if not uri:
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#dots)" opacity=".35"/>'
                f'<text class="b" x="{x + w / 2}" y="{y + h / 2}" font-size="14" text-anchor="middle" '
                f'fill="{GRAY}">картинка «{esc(key)}»</text>')
    align = ctx.images.align(key)
    return (f'<image class="zoom" href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'preserveAspectRatio="{align} slice"/>')


def focus_lines(rng: random.Random, cx, cy, rx, ry, count: int = 110, length: float = 900) -> str:
    """Линии концентрации (集中線): клинья от краёв к центру, середина остаётся чистой."""
    d = []
    for _ in range(count):
        a = rng.uniform(0, 2 * math.pi)
        k = rng.uniform(1.0, 1.6)
        ix, iy = cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k
        half = rng.uniform(0.004, 0.013)
        o1 = (cx + math.cos(a - half) * length, cy + math.sin(a - half) * length)
        o2 = (cx + math.cos(a + half) * length, cy + math.sin(a + half) * length)
        d.append(f"M{ix:.1f},{iy:.1f} L{o1[0]:.1f},{o1[1]:.1f} L{o2[0]:.1f},{o2[1]:.1f} Z")
    return f'<path class="flick" d="{" ".join(d)}" fill="{INK}"/>'


def bubble(cx, cy, rx, ry, tx, ty, spread: float = 0.17, stroke: float = 3) -> str:
    """Облачко-реплика: эллипс с хвостиком, указывающим на говорящего."""
    return speech_bubble(cx, cy, rx, ry, tx, ty, INK, stroke, "#fff", spread)


def tone(mid: str, x, y, w, h, pattern: str = "dots", fade: str = "fadeOut", opacity: float = 1.0) -> str:
    """Скринтон с плавным исчезновением (маска)."""
    return (f'<mask id="{mid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{fade})"/></mask>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pattern})" mask="url(#{mid})" '
            f'opacity="{opacity}"/>')


def hanko(T: Text, cx, cy, r, chars: str, delay: float = 1.2, rotate: float = -12) -> str:
    """Красная печать-ханко, «шлёпается» с задержкой."""
    size = r * 0.62 if len(chars) > 1 else r * 1.0
    if len(chars) > 1:
        glyphs = "".join(T.t(cx, cy - r * 0.06 + (i - (len(chars) - 1) / 2) * size * 1.02 + size * 0.36, ch,
                             f"{size:.0f}", RED, "middle") for i, ch in enumerate(chars))
    else:
        glyphs = T.t(cx, cy + size * 0.36, chars, f"{size:.0f}", RED, "middle")
    return (f'<g transform="rotate({rotate} {cx} {cy})"><g class="stamp" style="animation-delay:{delay}s">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" fill-opacity=".85" stroke="{RED}" stroke-width="3.5" '
            f'filter="url(#ink)"/><circle cx="{cx}" cy="{cy}" r="{r - 6}" fill="none" stroke="{RED}" '
            f'stroke-width="1.2"/>{glyphs}</g></g>')


WHITE_OUTLINE = 'stroke="#fff" stroke-width="10" paint-order="stroke" stroke-linejoin="round"'
INK_OUTLINE = f'stroke="{INK}" stroke-width="3" paint-order="stroke" stroke-linejoin="round"'
WHITE_HALO = 'stroke="#fff" stroke-width="6" paint-order="stroke" stroke-linejoin="round"'


def _fit(text: str, max_width: float, max_size: float, k: float) -> float:
    return min(max_size, max_width / (k * max(len(text), 1)))


# ---------------------------------------------------------------------------
# Шапка: страница из четырёх панелей
# ---------------------------------------------------------------------------


def header(cfg: dict, ctx) -> str:
    rng = random.Random(21)
    T = Text()
    w, h = 1200, 440
    greeting = cfg.get("greeting", "")
    title = cfg.get("title", "")
    subtitle = cfg.get("subtitle", "")
    title_size = _fit(title, 420, 66, 0.82)
    sub_size = _fit(subtitle, 370, 24, 0.5)
    g_rx = min(200, 30 + len(greeting) * 9.6)

    a = [(16, 16), (396, 16), (356, 424), (16, 424)]
    b = [(410, 16), (850, 16), (830, 286), (382, 286)]
    c = [(380, 300), (828, 300), (820, 424), (370, 424)]
    d = [(864, 16), (1184, 16), (1184, 424), (836, 424)]

    title_svg = T.t(616, 222, title, f"{title_size:.0f}", INK, "middle", WHITE_OUTLINE)
    sfx_svg = T.t(790, 128, "ドン！", 40, "#fff", "middle", INK_OUTLINE)
    panel_b = (
        f"{focus_lines(rng, 616, 196, 230, 70, 120)}"
        f'<g transform="rotate(-4 616 200)"><g class="shake">{title_svg}</g></g>'
        f'<g class="pop" style="animation-delay:.4s">{bubble(530, 70, g_rx, 34, 600, 134)}'
        f'{T.b(530, 77, greeting, 18, INK, "middle")}</g>'
        f'<g transform="rotate(12 790 116)"><g class="pop" style="animation-delay:.9s">{sfx_svg}</g></g>'
    )
    panel_c = (
        f'<rect x="370" y="300" width="460" height="124" fill="url(#dots)" opacity=".55"/>'
        f'<rect x="404" y="330" width="404" height="74" fill="#fff" stroke="{INK}" stroke-width="3"/>'
        f'<rect x="404" y="314" width="94" height="28" fill="{INK}"/>'
        f'{T.t(451, 334, "第1話", 15, "#fff", "middle")}'
        f'<g class="rise" style="animation-delay:.6s">{T.b(606, 375, subtitle, f"{sub_size:.0f}", INK, "middle")}</g>'
    )
    panel_d = (
        picture(ctx, "header_right", 836, 16, 348, 408)
        + f'<g transform="rotate(-8 900 92)">{T.b(900, 100, "ふぅ～", 24, INK, "middle")}</g>'
    )
    body = (
        f'<rect width="{w}" height="{h}" fill="#fff"/>'
        + panel("pa", a, picture(ctx, "header_left", 16, 16, 380, 408))
        + panel("pb", b, panel_b)
        + panel("pc", c, panel_c)
        + panel("pd", d, panel_d)
        + hanko(T, 368, 392, 38, "推し", 1.3)
    )
    return document(w, h, f"{title} — {subtitle}", DEFS, CSS, body, T.fonts(ctx))


# ---------------------------------------------------------------------------
# Разделитель: мазок туши
# ---------------------------------------------------------------------------


def divider(ctx) -> str:
    w, h = 900, 44
    body = (
        # белая «бумажная» обводка — чтобы мазок туши был виден и в тёмной теме GitHub
        f'<path class="draw" d="M40,22 C260,15 640,15 860,22 C640,28 260,29 40,22 Z" fill="{INK}" '
        f'stroke="#fff" stroke-width="3" stroke-linejoin="round" paint-order="stroke"/>'
        f'<circle cx="450" cy="22" r="14" fill="#fff" stroke="{INK}" stroke-width="2.5"/>'
        f'<g transform="translate(450,22) scale(1.05)"><path class="spin" d="{SPARKLE_PATH}" fill="{INK}"/></g>'
        f'<circle cx="372" cy="22" r="3" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        f'<circle cx="528" cy="22" r="3" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    )
    return document(w, h, "ink divider", DEFS, CSS, body)


# ---------------------------------------------------------------------------
# Подвал: «またね～» и «つづく…»
# ---------------------------------------------------------------------------


def footer(cfg: dict, ctx) -> str:
    rng = random.Random(9)
    T = Text()
    w, h = 1200, 280
    title = cfg.get("title", "")
    subtitle = cfg.get("subtitle", "")
    sub_size = _fit(subtitle, 360, 19, 0.56)
    left = [(16, 16), (330, 16), (310, 264), (16, 264)]
    mid = [(344, 16), (856, 16), (836, 264), (324, 264)]
    right = [(870, 16), (1184, 16), (1184, 264), (850, 264)]
    panel_mid = (
        f"{focus_lines(rng, 590, 140, 240, 92, 80)}"
        f'<g class="pop" style="animation-delay:.3s">{bubble(590, 130, 222, 84, 330, 214)}'
        f'{T.t(590, 134, title, 40, INK, "middle")}{T.b(590, 172, subtitle, f"{sub_size:.0f}", INK, "middle")}</g>'
    )
    arrow = "870,200 922,166 922,184 1170,184 1170,216 922,216 922,234"
    panel_right = (
        tone("fr", 850, 16, 334, 248, "dots", "fadeDown", .5)
        + T.t(1022, 84, "次回も", 26, INK, "middle")
        + T.t(1022, 120, "お楽しみに！", 26, INK, "middle")
        + T.b(1022, 148, "Продолжение следует…", 14, GRAY, "middle")
        + f'<g class="slide" style="animation-delay:.5s"><polygon points="{arrow}" fill="{INK}"/>'
        + T.t(1046, 208, "つづく…", 20, "#fff", "middle") + "</g>"
    )
    body = (
        f'<rect width="{w}" height="{h}" fill="#fff"/>'
        + panel("fl", left, picture(ctx, "footer", 16, 16, 314, 248))
        + panel("fm", mid, panel_mid)
        + panel("fr2", right, panel_right)
    )
    return document(w, h, f"{title} {subtitle}", DEFS, CSS, body, T.fonts(ctx))


# ---------------------------------------------------------------------------
# Окно статуса: лист персонажа из манги
# ---------------------------------------------------------------------------

_FILLS = [INK, "url(#hatch)", "url(#dotsBig)", "url(#dots)", "#c4c4c4"]


def status(stats: dict, derived: dict, cfg: dict, ctx, exclude: list | None = None,
           now: dt.datetime | None = None) -> str:
    T = Text()
    w, h = 900, 600
    now = now or dt.datetime.now(dt.timezone.utc)
    info = status_window.compute(stats, derived, cfg)
    fmt = status_window._fmt
    skills = status_window.skill_rows(stats, cfg, exclude)
    p: list[str] = []

    # шапка-плашка
    p.append(f'<rect x="8" y="8" width="884" height="56" fill="{INK}"/>')
    p.append(T.t(30, 47, "STATUS", 24, "#fff", extra='letter-spacing="6"'))
    p.append(T.b(196, 45, "ステータス", 18, "#fff"))
    p.append(T.b(872, 44, f"Обновлено: {now:%d.%m.%Y · %H:%M} UTC", 13, "#d0d0d0", "end", 400))

    # левая колонка: портрет и персонаж
    p.append(panel("sp", [(28, 82), (290, 82), (290, 344), (28, 344)], picture(ctx, "status", 28, 82, 262, 262, 560), 3))
    p.append(T.t(28, 384, truncate(stats["name"], 14), f"{_fit(truncate(stats['name'], 14), 200, 28, 0.78):.0f}"))
    p.append(T.b(28, 408, f"@{stats['login']}", 14, GRAY))
    p.append(hanko(T, 256, 384, 30, info["rank"], 0.9))
    p.append(f'<rect x="28" y="424" width="92" height="56" fill="{INK}"/>')
    p.append(T.t(74, 442, "LV", 11, "#fff", "middle", 'letter-spacing="3"'))
    p.append(T.t(74, 472, info["level"], 26, "#fff", "middle"))
    ratio = info["xp_into"] / info["xp_span"] if info["xp_span"] else 0
    p.append(T.t(134, 440, "EXP", 12))
    p.append(T.b(290, 440, f"{fmt(info['xp_into'])} / {fmt(info['xp_span'])}", 12, INK, "end"))
    p.append(f'<rect x="134" y="450" width="156" height="12" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    if ratio > 0:
        p.append(f'<rect class="grow" x="134" y="450" width="{max(156 * ratio, 4):.1f}" height="12" fill="{INK}"/>')
    p.append(T.b(134, 478, "до следующего уровня", 11, SOFT, weight=400))
    rows = [("Класс", info["class"]), ("Титул", f"«{info['title']}»"), ("Раса", info["race"]),
            ("Гильдия", f"GitHub · с {info['guild_year']} г.")]
    for i, (label, value) in enumerate(rows):
        y = 512 + i * 22
        p.append(T.b(28, y, label, 12, SOFT, weight=400))
        p.append(T.b(96, y, truncate(value, 27), 13))

    # правая колонка: характеристики
    p.append(T.t(316, 98, "能力値 · Характеристики", 15))
    cells = [("STR", "коммиты за год", stats["commits_year"]), ("INT", "пулл-реквесты", stats["prs_total"]),
             ("DEX", "issues", stats["issues_total"]), ("VIT", "макс. серия", derived["streak_longest"]),
             ("CHA", "подписчики", stats["followers"]), ("LUK", "звёзды", stats["stars"])]
    for i, (abbr, desc, value) in enumerate(cells):
        x, y = 316 + (i % 3) * 190, 112 + (i // 3) * 78
        p.append(f'<rect x="{x}" y="{y}" width="178" height="66" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
        p.append(f'<polygon points="{x},{y + 66} {x + 44},{y + 66} {x},{y + 36}" fill="url(#dots)" opacity=".8"/>')
        p.append(f'<rect x="{x}" y="{y}" width="50" height="22" fill="{INK}"/>')
        p.append(T.t(x + 25, y + 16, abbr, 12, "#fff", "middle"))
        p.append(T.b(x + 58, y + 16, desc, 11, GRAY, weight=400))
        p.append(T.t(x + 166, y + 56, fmt(value), 26, INK, "end"))

    bars = [("HP", "серия дней с коммитами", derived["streak_current"], max(derived["streak_longest"], 1),
             f"{derived['streak_current']} дн. · рекорд {derived['streak_longest']}", "url(#hatch)"),
            ("MP", "активных дней из 30", derived["active_days_30"], 30, f"{derived['active_days_30']} / 30",
             "url(#dotsBig)")]
    for i, (tag, desc, value, maximum, label, fill) in enumerate(bars):
        y = 288 + i * 46
        r = max(0.0, min(1.0, value / maximum)) if maximum else 0.0
        p.append(T.t(316, y, tag, 13))
        p.append(T.b(346, y, desc, 12, GRAY, weight=400))
        p.append(T.b(874, y, label, 12, INK, "end"))
        p.append(f'<rect x="316" y="{y + 8}" width="558" height="14" fill="#fff" stroke="{INK}" stroke-width="2"/>')
        if r > 0:
            p.append(f'<rect class="grow" style="animation-delay:{.3 + i * .2}s" x="317" y="{y + 9}" '
                     f'width="{max(556 * r, 4):.1f}" height="12" fill="{fill}"/>')

    p.append(T.t(316, 394, "スキル · Навыки", 15))
    if skills:
        step = 24 if len(skills) <= 5 else 21
        for i, sk in enumerate(skills):
            y = 420 + i * step
            fill = _FILLS[sk["group"] % len(_FILLS)]
            p.append(f'<rect x="316" y="{y - 11}" width="12" height="12" fill="{fill}" stroke="{INK}" stroke-width="1.5"/>')
            p.append(T.b(336, y, truncate(sk["name"], 16), 13))
            p.append(f'<rect x="470" y="{y - 10}" width="340" height="10" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
            p.append(f'<rect class="grow" style="animation-delay:{.4 + i * .1:.1f}s" x="471" y="{y - 9}" '
                     f'width="{max(338 * sk["ratio"], 3):.1f}" height="8" fill="{fill}"/>')
            p.append(T.b(874, y, sk["label"], 12, GRAY, "end"))
    else:
        p.append(T.b(316, 430, "Навыки ещё не раскрыты… (・_・;)", 14, GRAY))

    p.append(T.t(316, 554, "装備 · Снаряжение", 12))
    equipment = " · ".join(cfg.get("equipment", [])) or "Пока только палка и крышка от кастрюли"
    for i, line in enumerate(wrap(equipment, 56, 2)):
        p.append(T.b(316, 571 + i * 14, line, 11.5))
    weekly = derived["weekly"] or [0]
    p.append(T.t(874, 554, f"Журнал · {len(weekly)} нед." if derived["weekly"] else "Журнал", 11, INK, "end"))
    peak = max(weekly) or 1
    start = 874 - len(weekly) * 7.2 + 1.2
    for i, v in enumerate(weekly):
        bh = max(2.0, 22 * v / peak)
        p.append(f'<rect class="growY" style="animation-delay:{.5 + i * .03:.2f}s" x="{start + i * 7.2:.1f}" '
                 f'y="{584 - bh:.1f}" width="6" height="{bh:.1f}" fill="{INK if v == peak else "url(#hatch)"}" '
                 f'stroke="{INK}" stroke-width=".8"/>')

    body = ('<rect x="8" y="8" width="884" height="584" fill="#fff"/>' + "".join(p)
            + f'<rect x="8" y="8" width="884" height="584" fill="none" stroke="{INK}" stroke-width="5" '
              f'filter="url(#ink)"/>')
    return document(w, h, f"Статус: {stats['name']} — Lv. {info['level']}", DEFS, CSS, body, T.fonts(ctx))


# ---------------------------------------------------------------------------
# Цитата дня: персонаж говорит цитату в облачке
# ---------------------------------------------------------------------------


def quote(quotes: list[dict], ctx, day: dt.date | None = None, pinned: bool = False) -> str:
    T = Text()
    day = day or dt.datetime.now(dt.timezone.utc).date()
    _, q = pick(quotes, day)
    lines = balanced_wrap(q["text"], 32, 4)
    w = 900
    h = 300 if len(lines) <= 3 else 330
    cx, cy = 590, (h + 46) / 2
    ry = (h - 116) / 2
    text = "".join(T.b(cx, cy - (len(lines) - 1) * 14 + 7 + i * 28, line, 20, INK, "middle")
                   for i, line in enumerate(lines))
    body = (
        f'<rect x="8" y="8" width="{w - 16}" height="{h - 16}" fill="#fff"/>'
        + tone("qt", 286, 16, 598, h - 32, "dots", "fadeOut", .7)
        + panel("qp", [(24, 24), (274, 24), (274, h - 24), (24, h - 24)], picture(ctx, "quote", 24, 24, 250, h - 48, 560), 3)
        + f'<g transform="rotate(8 228 64)">{T.t(228, 72, "じーっ", 22, "#fff", "middle", INK_OUTLINE)}</g>'
        + f'<rect x="300" y="26" width="300" height="30" fill="{INK}"/>'
        + T.b(314, 47, PINNED_CAPTION if pinned else f"今日の名言 · {day:%d.%m.%Y}", 15, "#fff")
        + f'<g class="pop" style="animation-delay:.2s">{bubble(cx, cy, 274, ry, 280, cy + 30)}{text}</g>'
        + (T.b(874, h - 22, attribution(q), 16, INK, "end", extra=WHITE_HALO) if attribution(q) else "")
        + f'<rect x="8" y="8" width="{w - 16}" height="{h - 16}" fill="none" stroke="{INK}" stroke-width="5" '
          f'filter="url(#ink)"/>'
    )
    return document(w, h, f"{q['text']} {attribution(q)}".strip(), DEFS, CSS, body, T.fonts(ctx))


# ---------------------------------------------------------------------------
# «Сейчас смотрю»: обложки в ч/б панелях
# ---------------------------------------------------------------------------


def anime(data: dict, username: str, ctx, max_items: int = 5) -> str:
    from ..anime_list import _data_uri

    T = Text()
    w = 900
    items = data["items"][:max_items]
    h = 410 if items else 190
    p = [f'<rect x="8" y="8" width="884" height="{h - 16}" fill="#fff"/>',
         f'<rect x="8" y="8" width="884" height="52" fill="{INK}"/>',
         T.t(28, 44, "視聴中 · Сейчас смотрю", 20, "#fff"),
         T.b(872, 42, f"{data['service']} · {username}", 13, "#d0d0d0", "end"),
         T.b(28, 88, data["summary"], 13, GRAY, weight=400)]
    if not items:
        p.append(T.b(450, 140, "Сейчас ничего не смотрю… выбираю следующий тайтл (´・ω・`)", 16, INK, "middle"))
    col_w, gap = 164, 10
    x0 = (w - (len(items) * col_w + max(len(items) - 1, 0) * gap)) / 2
    for i, item in enumerate(items):
        cx = x0 + i * (col_w + gap) + col_w / 2
        ix, iy, iw, ih = cx - 64, 106, 128, 180
        uri = _data_uri(item["cover"])
        inner = (f'<image href="{uri}" x="{ix:.1f}" y="{iy}" width="{iw}" height="{ih}" filter="url(#gray)" '
                 f'preserveAspectRatio="xMidYMid slice"/>' if uri else
                 f'<rect x="{ix:.1f}" y="{iy}" width="{iw}" height="{ih}" fill="url(#dots)" opacity=".4"/>')
        p.append(f'<g class="rise" style="animation-delay:{i * .1:.1f}s">')
        p.append(panel(f"ac{i}", [(ix, iy), (ix + iw, iy), (ix + iw, iy + ih), (ix, iy + ih)], inner, 3))
        for j, line in enumerate(wrap(item["title"] or "???", 19, 2)):
            p.append(T.b(cx, iy + ih + 24 + j * 18, line, 13, INK, "middle"))
        total = item["total"]
        r = min(1.0, item["progress"] / total) if total else 0.0
        by = iy + ih + 66
        p.append(f'<rect x="{ix:.1f}" y="{by}" width="{iw}" height="8" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
        if r > 0:
            p.append(f'<rect class="grow" x="{ix + 1:.1f}" y="{by + 1}" width="{max((iw - 2) * r, 3):.1f}" '
                     f'height="6" fill="url(#hatch)"/>')
        p.append(T.b(cx, by + 26, f"эп. {item['progress']} / {total or '?'}", 12, GRAY, "middle", 400))
        p.append("</g>")
    p.append(f'<rect x="8" y="8" width="884" height="{h - 16}" fill="none" stroke="{INK}" stroke-width="5" '
             f'filter="url(#ink)"/>')
    return document(w, h, f"Сейчас смотрю ({data['service']})", DEFS, CSS, "".join(p), T.fonts(ctx))


# ---------------------------------------------------------------------------
# Подпись к счётчику просмотров: панель с облачком, которое указывает на девочек слева
# ---------------------------------------------------------------------------


def views_caption(cfg: dict, ctx) -> str:
    rng = random.Random(13)
    T = Text()
    w, h = 400, 130
    lines = balanced_wrap(cfg.get("caption", ""), 22, 2)
    cx, cy = 226, 70
    text = "".join(T.b(cx, cy - (len(lines) - 1) * 12 + 7 + i * 24, line, 20, INK, "middle")
                   for i, line in enumerate(lines))
    inner = (
        tone("vt", 30, 8, 362, 114, "dots", "fadeOut", .6)
        + focus_lines(rng, 236, 68, 150, 46, 70, 420)
        + f'<g transform="rotate(10 352 30)">{T.t(352, 36, "ワイワイ", 17, "#fff", "middle", INK_OUTLINE)}</g>'
    )
    body = (
        panel("vp", [(30, 8), (392, 8), (384, 122), (38, 122)], inner, 4)
        + f'<rect x="46" y="13" width="98" height="25" fill="{INK}"/>'
        + T.t(95, 31, cfg.get("tab", ""), 15, "#fff", "middle")
        + f'<g class="pop" style="animation-delay:.3s">{bubble(cx, cy, 150, 44, 4, 98)}{text}</g>'
    )
    return document(w, h, cfg.get("caption", ""), DEFS, CSS, body, T.fonts(ctx))
