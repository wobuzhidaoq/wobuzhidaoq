"""Статичные «декорации»: шапка с ночным небом и сакурой, разделитель и подвал."""

import random

from . import theme as t
from .fonts import FontEmbedder
from .svg import (PETAL_GRADIENT, SPARKLE_PATH, document, esc, falling_petals, flower,
                  petal_css)

# ---------------------------------------------------------------------------
# Общие элементы
# ---------------------------------------------------------------------------


def _stars(rng: random.Random, count: int, width: float, max_y: float) -> str:
    out = []
    for _ in range(count):
        x, y = rng.uniform(0, width), rng.uniform(0, max_y)
        r = rng.choice((0.6, 0.8, 1.0, 1.2, 1.5))
        out.append(
            f'<circle class="tw" cx="{x:.0f}" cy="{y:.0f}" r="{r}" '
            f'style="animation-duration:{rng.uniform(2, 5):.1f}s;'
            f'animation-delay:{-rng.uniform(0, 5):.1f}s"/>'
        )
    return "".join(out)


def _sparkles(rng: random.Random, spots: list[tuple[float, float, float]]) -> str:
    return "".join(
        f'<g transform="translate({x},{y}) scale({s})"><path class="tw" d="{SPARKLE_PATH}" '
        f'fill="{t.PINK_LIGHT}" style="animation-duration:{rng.uniform(2.5, 4.5):.1f}s;'
        f'animation-delay:{-rng.uniform(0, 4):.1f}s"/></g>'
        for x, y, s in spots
    )


_TWINKLE_CSS = """
.tw { fill: #fff6ff; animation: tw ease-in-out infinite; }
@keyframes tw { 0%, 100% { opacity: .25; } 50% { opacity: 1; } }
"""

# ---------------------------------------------------------------------------
# Шапка
# ---------------------------------------------------------------------------

_CAT = """
<g transform="translate({x},{y}) scale(.72)">
  <path fill="#0d0618" d="M-20,0 C-24,-16 -18,-34 -6,-38 L6,-38 C18,-34 24,-16 20,0 Z"/>
  <circle fill="#0d0618" cx="0" cy="-46" r="14"/>
  <path fill="#0d0618" d="M-12,-53 L-14,-70 L-3,-58 Z M12,-53 L14,-70 L3,-58 Z"/>
  <path fill="none" stroke="#0d0618" stroke-width="5" stroke-linecap="round"
        d="M17,-2 C32,0 38,-10 34,-24 C32,-32 36,-38 40,-40">
    <animateTransform attributeName="transform" type="rotate" values="0 17 -2; 14 17 -2; 0 17 -2"
                      dur="3.2s" repeatCount="indefinite"/>
  </path>
  <g filter="url(#softGlow)">
    <ellipse class="blink" cx="-5" cy="-47" rx="2.4" ry="3" fill="#ffe066"/>
    <ellipse class="blink" cx="5" cy="-47" rx="2.4" ry="3" fill="#ffe066"/>
  </g>
</g>
"""


def _torii(cx: float, base: float) -> str:
    dark = "#2a0b22"
    return f"""
<g>
  <rect x="{cx - 34}" y="{base - 80}" width="8" height="82" fill="{dark}"/>
  <rect x="{cx + 26}" y="{base - 80}" width="8" height="82" fill="{dark}"/>
  <rect x="{cx - 46}" y="{base - 62}" width="92" height="6" fill="{dark}"/>
  <rect x="{cx - 4}" y="{base - 78}" width="8" height="16" fill="{dark}"/>
  <rect x="{cx - 54}" y="{base - 84}" width="108" height="6" fill="{dark}"/>
  <path fill="{dark}" d="M{cx - 60},{base - 84} Q{cx},{base - 80} {cx + 60},{base - 84}
        L{cx + 70},{base - 97} Q{cx},{base - 90} {cx - 70},{base - 97} Z"/>
  <path fill="none" stroke="{t.PINK_DEEP}" stroke-opacity=".55" stroke-width="1.4"
        d="M{cx - 70},{base - 97} Q{cx},{base - 90} {cx + 70},{base - 97}"/>
</g>
"""


def _branch(rng: random.Random) -> str:
    wood = "#2b1424"
    strokes = [
        ("M-10,18 C50,28 120,66 228,62", 9),
        ("M228,62 C278,58 318,38 362,44", 5),
        ("M118,50 C138,82 162,98 200,100", 4),
        ("M58,30 C68,10 88,0 110,-6", 4),
        ("M300,50 C310,72 328,86 350,88", 3),
    ]
    paths = "".join(
        f'<path d="{d}" fill="none" stroke="{wood}" stroke-width="{w}" stroke-linecap="round"/>'
        for d, w in strokes
    )
    spots = [
        (228, 62, 1.2), (198, 56, 0.9), (258, 70, 1.0), (362, 44, 0.9), (336, 38, 0.7),
        (200, 100, 1.05), (176, 92, 0.75), (148, 76, 0.7), (110, -4, 1.0), (86, 10, 0.8),
        (350, 88, 0.9), (322, 82, 0.65), (40, 26, 0.8), (290, 48, 0.6),
    ]
    flowers = "".join(flower(x, y, s, rng.uniform(0, 72)) for x, y, s in spots)
    buds = "".join(
        f'<circle cx="{x}" cy="{y}" r="3" fill="{t.PINK}"/>'
        for x, y in ((140, 60), (276, 44), (310, 66), (70, 18), (380, 52))
    )
    return f'<g class="branch">{paths}{buds}{flowers}</g>'


def build_header(cfg: dict, fonts: FontEmbedder) -> str:
    rng = random.Random(7)
    w, h = 1200, 400
    greeting = cfg.get("greeting", "")
    title = cfg.get("title", "")
    subtitle = cfg.get("subtitle", "")
    title_size = min(88, int(560 / (0.6 * max(len(title), 1))))

    defs = f"""
<clipPath id="card"><rect width="{w}" height="{h}" rx="28"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{t.BG_DEEP}"/><stop offset=".45" stop-color="{t.BG_2}"/>
  <stop offset=".8" stop-color="#44195e"/><stop offset="1" stop-color="#6b2464"/>
</linearGradient>
<radialGradient id="moonGlow"><stop offset="0" stop-color="#ffe3f1" stop-opacity=".55"/>
  <stop offset=".5" stop-color="{t.PINK}" stop-opacity=".18"/><stop offset="1" stop-color="{t.PINK}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="moonBody" cx=".4" cy=".35"><stop offset="0" stop-color="#fffdf5"/>
  <stop offset="1" stop-color="#ffe2b0"/></radialGradient>
<linearGradient id="fuji" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4b2a7a"/>
  <stop offset="1" stop-color="#1e1040"/></linearGradient>
<linearGradient id="snow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fdf4ff"/>
  <stop offset="1" stop-color="#e3b8f0"/></linearGradient>
<linearGradient id="titleGrad" gradientUnits="userSpaceOnUse" x1="80" y1="0" x2="640" y2="0" spreadMethod="reflect">
  <stop offset="0" stop-color="{t.PINK_LIGHT}"/><stop offset=".35" stop-color="{t.PINK}"/>
  <stop offset=".7" stop-color="{t.LAVENDER}"/><stop offset="1" stop-color="{t.CYAN}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0; 560 0; 0 0"
                    dur="10s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="tail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="glow" x="-20%" y="-40%" width="140%" height="180%">
  <feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="softGlow" x="-200%" y="-200%" width="500%" height="500%">
  <feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="blur40"><feGaussianBlur stdDeviation="40"/></filter>
{PETAL_GRADIENT}
"""

    css = _TWINKLE_CSS + petal_css(h + 60) + """
.breathe { animation: breathe 7s ease-in-out infinite alternate; }
@keyframes breathe { from { opacity: .55; } to { opacity: 1; } }
.pulse { animation: pulse 5s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }
@keyframes pulse { from { transform: scale(.94); opacity: .8; } to { transform: scale(1.06); opacity: 1; } }
.shoot { animation: shoot 9s ease-in infinite; opacity: 0; }
@keyframes shoot {
  0% { transform: translate(0, 0); opacity: 0; } 2% { opacity: 1; }
  14% { transform: translate(-340px, 140px); opacity: 0; } 100% { transform: translate(-340px, 140px); opacity: 0; }
}
.branch { animation: branch 6s ease-in-out infinite alternate; transform-origin: 0 0; }
@keyframes branch { from { transform: rotate(-1.2deg); } to { transform: rotate(1.2deg); } }
.blink { animation: blink 5s infinite; transform-box: fill-box; transform-origin: center; }
@keyframes blink { 0%, 90%, 100% { transform: scaleY(1); } 94% { transform: scaleY(.1); } }
.firefly { animation: firefly ease-in-out infinite; }
@keyframes firefly {
  0% { transform: translate(0, 0); opacity: 0; } 30% { opacity: 1; }
  100% { transform: translate(24px, -70px); opacity: 0; }
}
.rise { animation: rise 1.4s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.shadow { paint-order: stroke fill; stroke: rgba(10, 8, 32, .65); stroke-width: 6px; stroke-linejoin: round; }
"""

    fireflies = "".join(
        f'<g transform="translate({rng.uniform(40, 1160):.0f},{rng.uniform(330, 390):.0f})">'
        f'<circle class="firefly" r="2" fill="{t.GOLD}" filter="url(#softGlow)" '
        f'style="animation-duration:{rng.uniform(4, 7):.1f}s;animation-delay:{-rng.uniform(0, 6):.1f}s"/></g>'
        for _ in range(12)
    )
    shooting = "".join(
        f'<g transform="translate({x},{y})"><g class="shoot" style="animation-delay:{d}s">'
        f'<line x1="0" y1="0" x2="130" y2="-54" stroke="url(#tail)" stroke-width="2" stroke-linecap="round"/>'
        f'<circle r="2.2" fill="#fff" filter="url(#softGlow)"/></g></g>'
        for x, y, d in ((760, 40, 1.5), (1150, 20, 6))
    )

    body = f"""
<g clip-path="url(#card)">
  <rect width="{w}" height="{h}" fill="url(#sky)"/>
  <g filter="url(#blur40)" class="breathe">
    <ellipse cx="380" cy="80" rx="330" ry="60" fill="{t.PINK_DEEP}" opacity=".16"/>
    <ellipse cx="780" cy="60" rx="300" ry="55" fill="{t.PURPLE}" opacity=".25"/>
  </g>
  {_stars(rng, 90, w, 270)}
  {_sparkles(rng, [(560, 40, .9), (660, 120, .6), (860, 210, .7), (1120, 70, .8), (470, 190, .5)])}
  {shooting}
  <circle class="pulse" cx="980" cy="122" r="170" fill="url(#moonGlow)"/>
  <circle cx="980" cy="122" r="74" fill="url(#moonBody)"/>
  <g fill="#f0d39b" opacity=".3">
    <circle cx="955" cy="100" r="11"/><circle cx="1003" cy="140" r="8"/><circle cx="990" cy="96" r="5"/>
    <circle cx="958" cy="150" r="6"/>
  </g>
  <path fill="#2a1650" opacity=".85" d="M0,350 L80,334 L150,342 L230,322 L300,336 L380,318 L450,332 L520,312
        L600,326 L860,318 L930,300 L1000,316 L1080,296 L1150,312 L1200,304 L1200,400 L0,400 Z"/>
  <path fill="url(#fuji)" d="M500,400 C560,350 620,290 668,246 C690,226 704,214 720,213 C736,214 752,226 774,246
        C822,290 882,350 940,400 Z"/>
  <path fill="url(#snow)" d="M668,246 C690,226 704,214 720,213 C736,214 752,226 774,246 L762,252 L750,244 L738,262
        L726,248 L714,264 L702,247 L690,258 L680,248 Z"/>
  <path fill="#120a26" d="M0,400 L0,352 C120,330 220,345 330,350 C450,356 520,338 610,348 C700,358 780,344
        880,338 C960,333 1000,330 1060,336 C1120,342 1170,338 1200,334 L1200,400 Z"/>
  {_torii(1010, 338)}
  {_CAT.format(x=1050, y=244)}
  {fireflies}
  {_branch(rng)}
  {falling_petals(rng, 26, w, h)}
  <g>
    <g class="rise" style="animation-delay:.1s">
      <g transform="translate(92,160) scale(.9)"><path d="{SPARKLE_PATH}" fill="{t.PINK}"/></g>
      <text x="112" y="168" font-size="26" font-weight="500" fill="{t.PINK_LIGHT}" letter-spacing="2"
            class="shadow">{esc(greeting)}</text>
    </g>
    <g class="rise" style="animation-delay:.35s">
      <text x="80" y="252" font-size="{title_size}" font-weight="800" fill="url(#titleGrad)"
            filter="url(#glow)" class="shadow">{esc(title)}</text>
    </g>
    <g class="rise" style="animation-delay:.6s">
      <text x="84" y="298" font-size="24" font-weight="500" fill="{t.TEXT}" class="shadow">{esc(subtitle)}</text>
    </g>
  </g>
</g>
"""
    font_css = fonts.css(greeting + title + subtitle, (500, 800))
    return document(w, h, f"{title} — {subtitle}", defs, css, body, font_css)


# ---------------------------------------------------------------------------
# Разделитель
# ---------------------------------------------------------------------------


def build_divider() -> str:
    rng = random.Random(3)
    w, h = 900, 44
    defs = f"""
<linearGradient id="line" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="860" y2="0">
  <stop offset="0" stop-color="{t.PINK}" stop-opacity="0"/><stop offset=".3" stop-color="{t.PINK}"/>
  <stop offset=".7" stop-color="{t.LAVENDER}"/><stop offset="1" stop-color="{t.LAVENDER}" stop-opacity="0"/>
</linearGradient>
{PETAL_GRADIENT}
"""
    css = _TWINKLE_CSS + """
.rot { animation: rot 14s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes rot { to { transform: rotate(360deg); } }
"""
    body = f"""
<path d="M40,22 H418 M482,22 H860" stroke="url(#line)" stroke-width="1.6" stroke-linecap="round"/>
<g class="rot">{flower(450, 22, 0.95)}</g>
{flower(300, 22, 0.42, 20)}{flower(600, 22, 0.42, 50)}
{_sparkles(rng, [(375, 22, .55), (525, 22, .55), (180, 22, .4), (720, 22, .4)])}
"""
    return document(w, h, "sakura divider", defs, css, body)


# ---------------------------------------------------------------------------
# Подвал
# ---------------------------------------------------------------------------


def _wave(y: float, amp: float, length: float, width: float) -> str:
    """Синусоподобная волна шириной 2*width — её можно бесшовно сдвигать на width."""
    d = f"M0,{y}"
    x = 0.0
    up = True
    while x < width * 2:
        d += f" q{length / 2},{-amp if up else amp} {length},0"
        x += length
        up = not up
    return d + " V200 H0 Z"


def build_footer(cfg: dict, fonts: FontEmbedder) -> str:
    rng = random.Random(11)
    w, h = 1200, 190
    title = cfg.get("title", "")
    subtitle = cfg.get("subtitle", "")
    defs = f"""
<clipPath id="card"><rect width="{w}" height="{h}" rx="28"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{t.BG_2}"/><stop offset="1" stop-color="{t.BG_DEEP}"/>
</linearGradient>
<filter id="glow" x="-20%" y="-60%" width="140%" height="220%">
  <feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
{PETAL_GRADIENT}
"""
    css = _TWINKLE_CSS + petal_css(h + 40, -120) + """
.wave { animation: wave linear infinite; }
@keyframes wave { to { transform: translateX(-1200px); } }
.rise { animation: rise 1.4s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
"""
    waves = "".join(
        f'<path class="wave" d="{_wave(y, amp, 150, w)}" fill="{fill}" opacity="{op}" '
        f'style="animation-duration:{dur}s"/>'
        for y, amp, fill, op, dur in (
            (150, 10, t.PURPLE, 0.25, 26),
            (160, 8, t.PINK_DEEP, 0.18, 18),
            (170, 6, "#0a0820", 0.9, 12),
        )
    )
    body = f"""
<g clip-path="url(#card)">
  <rect width="{w}" height="{h}" fill="url(#sky)"/>
  {_stars(rng, 60, w, 140)}
  {flower(130, 70, 1.3, 10)}{flower(1070, 64, 1.1, 40)}{flower(1110, 104, .7, 5)}{flower(92, 112, .7, 30)}
  {falling_petals(rng, 14, w, h, 0.4, 0.8)}
  <g class="rise">
    <text x="600" y="84" text-anchor="middle" font-size="40" font-weight="800" fill="{t.PINK}"
          filter="url(#glow)">{esc(title)}</text>
    <text x="600" y="120" text-anchor="middle" font-size="19" font-weight="500" fill="{t.TEXT}"
          opacity=".9">{esc(subtitle)}</text>
  </g>
  {waves}
</g>
"""
    font_css = fonts.css(title + subtitle, (500, 800))
    return document(w, h, f"{title} {subtitle}", defs, css, body, font_css)


# ---------------------------------------------------------------------------
# Заглушка для карточек, которые ещё не сгенерированы
# ---------------------------------------------------------------------------


def build_placeholder(w: int, h: int, label: str, fonts: FontEmbedder) -> str:
    size = max(12, int(min(w / max(len(label), 1) * 1.6, w / 20)))
    defs = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#1a1140"/><stop offset="1" stop-color="#0d0a24"/></linearGradient>
{PETAL_GRADIENT}
"""
    css = """
.rot { animation: rot 6s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes rot { to { transform: rotate(360deg); } }
"""
    body = f"""
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" fill="url(#bg)" stroke="{t.LAVENDER}"
      stroke-opacity=".4" stroke-dasharray="6 6"/>
<g class="rot">{flower(w / 2, h / 2 - size * 0.9 - 8, max(1.2, size / 16))}</g>
<text x="{w / 2}" y="{h / 2 + size * 0.9:.0f}" text-anchor="middle" font-size="{size}" font-weight="500"
      fill="{t.MUTED}">{esc(label)}</text>
"""
    return document(w, h, label, defs, css, body, fonts.css(label, (500,)))
