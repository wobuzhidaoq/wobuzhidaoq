"""Декорации: шапка с дневной сакурой, разделитель, подвал с котиками, «луговая» подложка карточек."""

import random

from . import art
from . import theme as t
from .fonts import FontEmbedder
from .svg import PETAL_GRADIENT, document, esc, falling_petals, flower, petal_css

_TEXT_CSS = """
.rise { animation: rise 1.4s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.halo { paint-order: stroke fill; stroke: #ffffff; stroke-linejoin: round; }
"""

# ---------------------------------------------------------------------------
# Шапка
# ---------------------------------------------------------------------------


def build_header(cfg: dict, fonts: FontEmbedder) -> str:
    rng = random.Random(7)
    w, h = 1200, 400
    greeting = cfg.get("greeting", "")
    title = cfg.get("title", "")
    subtitle = cfg.get("subtitle", "")
    title_size = min(88, int(560 / (0.6 * max(len(title), 1))))

    far = '<path fill="#b9dcef" opacity=".8" d="M0,318 L90,292 L170,304 L260,276 L350,298 L430,284 L520,300 L600,290 L700,300 L1200,290 L1200,400 L0,400 Z"/>'
    back = art.Hill((0, 312), [((160, 292), (330, 304), (520, 298)), ((700, 292), (860, 280), (1200, 284))], w, h)
    main = art.Hill((0, 340), [((180, 330), (330, 338), (480, 324)), ((640, 308), (760, 288), (900, 270)),
                               ((1000, 258), (1100, 252), (1200, 250))], w, h)
    cat_x = 880
    defs = f"""
<clipPath id="card"><rect width="{w}" height="{h}" rx="28"/></clipPath>
{art.ART_DEFS}
{PETAL_GRADIENT}
<linearGradient id="titleGrad" gradientUnits="userSpaceOnUse" x1="80" y1="0" x2="640" y2="0" spreadMethod="reflect">
  <stop offset="0" stop-color="{t.ACCENT}"/><stop offset=".4" stop-color="#ff7eb6"/>
  <stop offset=".75" stop-color="#c77dff"/><stop offset="1" stop-color="#ff5fa2"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0; 560 0; 0 0"
                    dur="10s" repeatCount="indefinite"/>
</linearGradient>
<filter id="titleShadow" x="-10%" y="-30%" width="120%" height="160%">
  <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#ff4f9a" flood-opacity=".35"/>
</filter>
"""
    css = art.ART_CSS + petal_css(h + 60) + _TEXT_CSS
    body = f"""
<g clip-path="url(#card)">
  <rect width="{w}" height="{h}" fill="url(#skyDay)"/>
  {art.sun(120, 26)}
  {art.cloud(560, 80, .6, 40)}{art.cloud(700, 150, .45, 55)}{art.cloud(330, 60, .5, 48)}
  {far}
  {back.path("url(#hillBack)")}
  {art.cloud(610, 284, 1.25, 60)}{art.cloud(780, 268, .9, 50)}{art.cloud(30, 318, 1.0, 70)}
  {main.path("url(#hill)")}
  {main.flowers(rng, 40)}
  {main.petals(rng, 140)}
  {main.grass(rng)}
  {art.sakura_tree(rng, 1010, main.y_at(1010) + 6)}
  {art.cat_sitting(cat_x, main.y_at(cat_x) + 4, 0.95)}
  {art.butterfly("M700,250 C760,200 820,230 860,190 C900,150 960,200 920,240 C880,280 760,300 700,250 Z", 14)}
  {art.butterfly("M200,200 C260,170 320,210 380,180 C430,160 420,230 360,240 C300,250 240,240 200,200 Z", 17,
                 "#c9b6ff", "#ffffff")}
  {art.sparkles(rng, [(180, 90, 1.2), (300, 140, .7), (90, 180, .8), (840, 60, .9), (1100, 160, .8),
                      (960, 30, 1), (420, 40, .6), (1160, 90, .6)])}
  {falling_petals(rng, 30, w, h)}
  <g class="rise" style="animation-delay:.1s">
    {flower(96, 157, .8)}
    <text x="118" y="166" font-size="27" font-weight="800" fill="{t.ACCENT}" stroke-width="7" class="halo"
          letter-spacing="2">{esc(greeting)}</text>
  </g>
  <g class="rise" style="animation-delay:.35s">
    <text x="78" y="254" font-size="{title_size}" font-weight="800" fill="url(#titleGrad)" stroke-width="12"
          class="halo" filter="url(#titleShadow)">{esc(title)}</text>
  </g>
  <g class="rise" style="animation-delay:.6s">
    <text x="84" y="302" font-size="24" font-weight="800" fill="{t.INK}" stroke-width="7"
          class="halo">{esc(subtitle)}</text>
  </g>
</g>
"""
    font_css = fonts.css(greeting + title + subtitle, (800,))
    return document(w, h, f"{title} — {subtitle}", defs, css, body, font_css)


# ---------------------------------------------------------------------------
# Разделитель с маленьким кои
# ---------------------------------------------------------------------------


def build_divider() -> str:
    rng = random.Random(3)
    w, h = 900, 50
    defs = f"""
<linearGradient id="line" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="860" y2="0">
  <stop offset="0" stop-color="{t.PINK}" stop-opacity="0"/><stop offset=".3" stop-color="{t.PINK}"/>
  <stop offset=".7" stop-color="{t.SKY}"/><stop offset="1" stop-color="{t.SKY}" stop-opacity="0"/>
</linearGradient>
{art.ART_DEFS}
{PETAL_GRADIENT}
"""
    css = art.ART_CSS + """
.rot { animation: rot 14s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes rot { to { transform: rotate(360deg); } }
"""
    swim = "M120,25 C300,14 600,36 780,25 C600,40 300,10 120,25 Z"
    body = f"""
<path d="M40,25 H418 M482,25 H860" stroke="url(#line)" stroke-width="2" stroke-linecap="round"/>
{art.koi("kohaku", swim, 22, .42)}
<g class="rot">{flower(450, 25, 1.0)}</g>
{flower(300, 25, 0.45, 20)}{flower(600, 25, 0.45, 50)}
{art.sparkles(rng, [(375, 25, .55), (525, 25, .55), (180, 25, .45), (720, 25, .45)], "#ffb000")}
"""
    return document(w, h, "sakura divider", defs, css, body)


# ---------------------------------------------------------------------------
# Подвал: луг, манэки-нэко машет лапкой, рядом спит котик
# ---------------------------------------------------------------------------


def build_footer(cfg: dict, fonts: FontEmbedder) -> str:
    rng = random.Random(11)
    w, h = 1200, 240
    title = cfg.get("title", "")
    subtitle = cfg.get("subtitle", "")
    hill = art.Hill((0, 196), [((300, 180), (600, 192), (900, 182)), ((1000, 178), (1100, 184), (1200, 180))], w, h)
    defs = f"""
<clipPath id="card"><rect width="{w}" height="{h}" rx="28"/></clipPath>
{art.ART_DEFS}
{PETAL_GRADIENT}
"""
    css = art.ART_CSS + petal_css(h + 40, -120) + _TEXT_CSS
    body = f"""
<g clip-path="url(#card)">
  <rect width="{w}" height="{h}" fill="url(#skyDay)"/>
  {art.sun(1130, 10)}
  {art.cloud(260, 70, .7, 45)}{art.cloud(820, 50, .55, 60)}{art.cloud(1010, 120, .5, 50)}
  {hill.path("url(#hill)")}
  {hill.flowers(rng, 30, (8, 40))}
  {hill.petals(rng, 70, (6, 50))}
  {hill.grass(rng)}
  {art.maneki_neko(170, hill.y_at(170) + 8, 1.05)}
  {art.cat_sleeping(1030, hill.y_at(1030) + 8, 0.95)}
  {flower(90, 40, 1.2, 10)}{flower(1150, 200, .9, 30)}
  {falling_petals(rng, 16, w, h, 0.4, 0.8)}
  <g class="rise">
    <text x="600" y="96" text-anchor="middle" font-size="44" font-weight="800" fill="{t.ACCENT}"
          stroke-width="9" class="halo">{esc(title)}</text>
    <text x="600" y="136" text-anchor="middle" font-size="20" font-weight="800" fill="{t.INK}"
          stroke-width="6" class="halo">{esc(subtitle)}</text>
  </g>
</g>
"""
    font_css = fonts.css(title + subtitle + "zZ", (800,))
    return document(w, h, f"{title} {subtitle}", defs, css, body, font_css)


# ---------------------------------------------------------------------------
# Луговая подложка для карточек: небо, облака, трава снизу, полупрозрачное «стекло» под текст
# ---------------------------------------------------------------------------


def meadow_card(rng: random.Random, w: int, h: int, top: int = 0, grass_h: int = 34,
                card_id: str = "card") -> str:
    """Фон карточки (x=8..w-8, y=top+8..h-8). Возвращает SVG; контент рисуется поверх."""
    x0, y0, cw, ch = 8, top + 8, w - 16, h - top - 16
    ground = y0 + ch - grass_h
    hill = art.Hill((x0, ground), [((x0 + cw * .3, ground - 8), (x0 + cw * .6, ground + 4),
                                    (x0 + cw, ground - 6))], w, h)
    return f"""
<clipPath id="{card_id}"><rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="22"/></clipPath>
<rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="22" fill="#ffffff" stroke="url(#border)" stroke-width="6"
      filter="url(#softBlur)" opacity=".7"/>
<g clip-path="url(#{card_id})">
  <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" fill="url(#skySoft)"/>
  {art.cloud(x0 + cw * .18, y0 + 34, .45, 50)}{art.cloud(x0 + cw * .62, y0 + 60, .38, 60)}
  {art.cloud(x0 + cw * .88, y0 + 26, .32, 44)}
  {hill.path("url(#hill)")}
  {hill.flowers(rng, int(cw / 40), (6, grass_h))}
  {hill.petals(rng, int(cw / 14), (4, grass_h))}
  {hill.grass(rng, 5)}
  {falling_petals(rng, 9, w, h, 0.4, 0.7, 0.85)}
</g>
<rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="22" fill="none" stroke="url(#border)" stroke-width="2"/>
"""


CARD_DEFS = f"""
<linearGradient id="border" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset=".5" stop-color="{t.LILAC}"/>
  <stop offset="1" stop-color="{t.SKY}"/></linearGradient>
<linearGradient id="hline" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset=".6" stop-color="{t.LILAC}"/>
  <stop offset="1" stop-color="{t.SKY}" stop-opacity="0"/></linearGradient>
"""


def glass(x: float, y: float, w: float, h: float, opacity: float = .84) -> str:
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#ffffff" fill-opacity="{opacity}" '
            f'stroke="#ffffff" stroke-width="1.5"/>')


# ---------------------------------------------------------------------------
# Заглушка для карточек, которые ещё не сгенерированы
# ---------------------------------------------------------------------------


def build_placeholder(w: int, h: int, label: str, fonts: FontEmbedder) -> str:
    rng = random.Random(w * h)
    size = max(12, int(min(w / max(len(label), 1) * 1.6, w / 20)))
    defs = art.ART_DEFS + PETAL_GRADIENT + CARD_DEFS
    css = art.ART_CSS + petal_css(h + 40, -100) + """
.rot { animation: rot 6s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes rot { to { transform: rotate(360deg); } }
"""
    body = f"""
{meadow_card(rng, w, h, grass_h=max(24, h // 7))}
<g class="rot">{flower(w / 2, h / 2 - size * 0.9 - 8, max(1.2, size / 16))}</g>
<text x="{w / 2}" y="{h / 2 + size * 0.9:.0f}" text-anchor="middle" font-size="{size}" font-weight="800"
      fill="{t.INK}" stroke="#ffffff" stroke-width="{max(3, size // 5)}" style="paint-order: stroke fill"
      stroke-linejoin="round">{esc(label)}</text>
"""
    return document(w, h, label, defs, css, body, fonts.css(label, (800,)))
