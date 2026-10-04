"""Рисованные элементы сцены: облака, солнце, дерево сакуры, трава, котики, карпы кои.

Каждая функция возвращает кусок SVG. Нужные градиенты/клипы лежат в ART_DEFS,
нужные анимации — в ART_CSS: их надо добавить в документ, где используются элементы.
"""

import math
import random

from . import theme as t
from .svg import PETAL_PATH, SPARKLE_PATH, flower

OUTLINE = "#5a3d35"

ART_DEFS = """
<linearGradient id="skyDay" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#78c6ff"/><stop offset=".55" stop-color="#bfe7ff"/>
  <stop offset="1" stop-color="#eef9ff"/></linearGradient>
<linearGradient id="skySoft" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#cdeeff"/><stop offset="1" stop-color="#f4fbff"/></linearGradient>
<linearGradient id="hill" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#b8ec88"/><stop offset=".35" stop-color="#7fd062"/>
  <stop offset="1" stop-color="#4caf50"/></linearGradient>
<linearGradient id="hillBack" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#cdeeb4"/><stop offset="1" stop-color="#9fd98e"/></linearGradient>
<linearGradient id="trunk" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#6b3f30"/><stop offset=".5" stop-color="#8d5a43"/>
  <stop offset="1" stop-color="#5c3427"/></linearGradient>
<radialGradient id="sunGlow"><stop offset="0" stop-color="#ffffff" stop-opacity=".95"/>
  <stop offset=".18" stop-color="#fff8d6" stop-opacity=".8"/>
  <stop offset=".5" stop-color="#fff3c4" stop-opacity=".25"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</radialGradient>
<linearGradient id="ray" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#ffffff" stop-opacity=".75"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</linearGradient>
<linearGradient id="water" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#9fe6f2"/><stop offset=".5" stop-color="#55bde0"/>
  <stop offset="1" stop-color="#3496c8"/></linearGradient>
<clipPath id="koiBody"><path d="M34,0 C30,-10 14,-14 0,-12 C-14,-10 -24,-6 -30,0 C-24,6 -14,10 0,12 C14,14 30,10 34,0 Z"/></clipPath>
<filter id="softBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="shine" x="-200%" y="-200%" width="500%" height="500%">
  <feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
"""

ART_CSS = """
.tw { animation: tw ease-in-out infinite; }
@keyframes tw { 0%, 100% { opacity: .2; } 50% { opacity: 1; } }
.drift { animation: drift ease-in-out infinite alternate; }
@keyframes drift { from { transform: translateX(-30px); } to { transform: translateX(30px); } }
.rays { animation: rays 9s ease-in-out infinite alternate; transform-box: view-box; }
@keyframes rays { from { opacity: .55; } to { opacity: 1; } }
.treeSway { animation: treeSway 6s ease-in-out infinite alternate; transform-box: view-box; }
@keyframes treeSway { from { transform: rotate(-.6deg); } to { transform: rotate(.6deg); } }
.blink { animation: blink 4.5s infinite; transform-box: fill-box; transform-origin: center; }
@keyframes blink { 0%, 92%, 100% { transform: scaleY(1); } 95% { transform: scaleY(.1); } }
.flap { animation: flap .35s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }
@keyframes flap { from { transform: scaleX(1); } to { transform: scaleX(.25); } }
.ripple { animation: ripple 4s ease-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes ripple { from { transform: scale(.2); opacity: .7; } to { transform: scale(1.6); opacity: 0; } }
.float { animation: float 7s ease-in-out infinite alternate; }
@keyframes float { from { transform: translate(-6px, -3px) rotate(-8deg); } to { transform: translate(6px, 3px) rotate(8deg); } }
.zzz { animation: zzz 3.5s ease-out infinite; }
@keyframes zzz { from { transform: translate(0, 0); opacity: 0; } 20% { opacity: 1; } to { transform: translate(14px, -26px); opacity: 0; } }
"""


# ---------------------------------------------------------------------------
# Небо
# ---------------------------------------------------------------------------


def cloud(x: float, y: float, s: float, drift_s: float | None = None) -> str:
    parts = ((0, 0, 26), (28, -16, 32), (62, -8, 28), (88, 4, 20), (-24, 6, 18))
    circles = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>' for cx, cy, r in parts)
    base = '<rect x="-40" y="0" width="148" height="24" rx="12"/>'
    shape = (f'<g fill="#d3e8fb" transform="translate(0,6)">{circles}{base}</g>'
             f'<g fill="#ffffff">{circles}{base}</g>')
    inner = (f'<g class="drift" style="animation-duration:{drift_s}s">{shape}</g>' if drift_s else shape)
    return f'<g transform="translate({x},{y}) scale({s})">{inner}</g>'


def sun(cx: float, cy: float) -> str:
    rays = "".join(
        f'<polygon points="0,0 900,{-w} 900,{w}" fill="url(#ray)" transform="rotate({a})" opacity="{o}"/>'
        for a, w, o in ((8, 26, .5), (20, 40, .7), (31, 22, .45), (42, 50, .65), (55, 28, .5),
                        (66, 44, .55), (78, 24, .4), (90, 36, .35))
    )
    return (f'<g transform="translate({cx},{cy})"><g class="rays">{rays}</g></g>'
            f'<circle cx="{cx}" cy="{cy}" r="260" fill="url(#sunGlow)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="34" fill="#ffffff" filter="url(#softBlur)"/>')


def sparkles(rng: random.Random, spots, color: str = "#ffffff") -> str:
    return "".join(
        f'<g transform="translate({x},{y}) scale({s})"><path class="tw" d="{SPARKLE_PATH}" fill="{color}" '
        f'filter="url(#shine)" style="animation-duration:{rng.uniform(2.2, 4.5):.1f}s;'
        f'animation-delay:{-rng.uniform(0, 4):.1f}s"/></g>'
        for x, y, s in spots
    )


def butterfly(path: str, dur: float, wing: str = "#ffb3d1", wing2: str = "#ffe08a", scale: float = 1.6) -> str:
    return (
        f'<g><animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}"/><g transform="scale({scale})">'
        f'<g class="flap">'
        f'<ellipse cx="-6" cy="-4" rx="7" ry="5" fill="{wing}" stroke="{OUTLINE}" stroke-width="1"/>'
        f'<ellipse cx="6" cy="-4" rx="7" ry="5" fill="{wing}" stroke="{OUTLINE}" stroke-width="1"/>'
        f'<ellipse cx="-4" cy="4" rx="4.5" ry="4" fill="{wing2}" stroke="{OUTLINE}" stroke-width="1"/>'
        f'<ellipse cx="4" cy="4" rx="4.5" ry="4" fill="{wing2}" stroke="{OUTLINE}" stroke-width="1"/>'
        f'</g><rect x="-1.2" y="-7" width="2.4" height="13" rx="1.2" fill="{OUTLINE}"/></g></g>'
    )


# ---------------------------------------------------------------------------
# Холм с травой
# ---------------------------------------------------------------------------


def _bezier(p0, p1, p2, p3, n):
    pts = []
    for i in range(n + 1):
        u = i / n
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


class Hill:
    """Холм из кубических кривых: умеет рисовать себя, траву, цветочки и лепестки на склоне."""

    def __init__(self, start: tuple[float, float], curves: list[tuple], width: float, height: float):
        self.start, self.curves, self.width, self.height = start, curves, width, height
        pts, cur = [], start
        for c in curves:
            pts += _bezier(cur, c[0], c[1], c[2], 40)
            cur = c[2]
        self.points = sorted(pts)

    def y_at(self, x: float) -> float:
        pts = self.points
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * ((x - x0) / (x1 - x0) if x1 != x0 else 0)
        return pts[-1][1]

    def path(self, fill: str) -> str:
        d = f"M0,{self.height} L{self.start[0]},{self.start[1]} " + " ".join(
            f"C{a[0]},{a[1]} {b[0]},{b[1]} {c[0]},{c[1]}" for a, b, c in self.curves
        ) + f" L{self.width},{self.height} Z"
        return f'<path d="{d}" fill="{fill}"/>'

    def grass(self, rng: random.Random, step: float = 6.0) -> str:
        out = []
        x = 0.0
        while x <= self.width:
            y = self.y_at(x)
            h = rng.uniform(7, 15)
            lean = rng.uniform(-5, 5)
            color = rng.choice(("#4fa84f", "#5cb85c", "#6cc65e", "#3f9a47"))
            out.append(f'<path d="M{x:.1f},{y + 3:.1f} q{lean / 2:.1f},{-h / 2:.1f} {lean:.1f},{-h:.1f}" '
                       f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" fill="none"/>')
            x += rng.uniform(step * 0.5, step * 1.3)
        return "".join(out)

    def scatter(self, rng: random.Random, count: int, depth: tuple[float, float]):
        for _ in range(count):
            x = rng.uniform(0, self.width)
            yield x, self.y_at(x) + rng.uniform(*depth)

    def petals(self, rng: random.Random, count: int, depth=(6, 120)) -> str:
        return "".join(
            f'<path d="{PETAL_PATH}" fill="{rng.choice(("#ffc2dc", "#ffa6cc", "#ffd6e8", "#ff9ec7"))}" '
            f'transform="translate({x:.0f},{y:.0f}) rotate({rng.uniform(0, 360):.0f}) '
            f'scale({rng.uniform(.35, .6):.2f},{rng.uniform(.2, .35):.2f})"/>'
            for x, y in self.scatter(rng, count, depth)
        )

    def flowers(self, rng: random.Random, count: int, depth=(10, 100)) -> str:
        out = []
        for x, y in self.scatter(rng, count, depth):
            color = rng.choice(("#ffffff", "#fff6a8", "#ffd1e6"))
            dots = "".join(f'<circle cx="{math.cos(a) * 2.6:.1f}" cy="{math.sin(a) * 2.6:.1f}" r="2"/>'
                           for a in (i * 2 * math.pi / 5 for i in range(5)))
            out.append(f'<g transform="translate({x:.0f},{y:.0f})" fill="{color}">{dots}'
                       f'<circle r="1.6" fill="#ffb000"/></g>')
        return "".join(out)


# ---------------------------------------------------------------------------
# Дерево сакуры
# ---------------------------------------------------------------------------


def sakura_tree(rng: random.Random, x: float, y: float, scale: float = 1.0) -> str:
    trunk = ('<path fill="url(#trunk)" d="M-34,4 C-20,-28 -14,-70 -16,-100 L8,-100 C8,-68 14,-30 34,4 '
             'C18,0 10,-2 0,0 C-12,-2 -22,0 -34,4 Z"/>')
    branches = [
        ("M-10,-94 C-30,-130 -60,-154 -110,-172", 14), ("M0,-94 C20,-134 60,-166 110,-190", 14),
        ("M-6,-100 C-4,-140 -10,-180 -20,-220", 11), ("M-80,-162 C-110,-180 -150,-184 -190,-178", 7),
        ("M80,-178 C110,-200 140,-206 180,-204", 7), ("M-50,-146 C-70,-130 -100,-120 -140,-122", 6),
        ("M50,-158 C80,-146 110,-132 150,-130", 6),
    ]
    wood = "".join(f'<path d="{d}" fill="none" stroke="#714334" stroke-width="{w}" stroke-linecap="round"/>'
                   for d, w in branches)
    clusters = [(-110, -180, 90), (-190, -168, 70), (-140, -118, 58), (-20, -232, 95), (110, -196, 90),
                (186, -210, 72), (152, -128, 60), (40, -160, 70), (-62, -212, 72), (-20, -150, 55),
                (60, -112, 46), (-88, -108, 46), (232, -160, 52), (-236, -148, 50), (70, -250, 70)]
    blobs = []
    for cx, cy, r in clusters:
        for _ in range(22):
            a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0, r * 0.75)
            blobs.append((cx + math.cos(a) * d, cy + math.sin(a) * d * 0.8, rng.uniform(0.28, 0.45) * r))
    layers = []
    for color, dx, dy, k in (("#f58fb9", 7, 9, 1.0), ("#ffb0d0", 0, 0, 0.95), ("#ffcfe3", -6, -8, 0.7),
                             ("#ffe9f3", -10, -14, 0.35)):
        layers.append("".join(f'<circle cx="{bx + dx:.0f}" cy="{by + dy:.0f}" r="{br * k:.0f}" fill="{color}"/>'
                              for bx, by, br in blobs))
    blossoms = "".join(flower(rng.uniform(-240, 240), rng.uniform(-300, -110), rng.uniform(.4, .7),
                              rng.uniform(0, 72), "#fff4f9") for _ in range(26))
    return (f'<g transform="translate({x},{y}) scale({scale})">'
            f'<g class="treeSway" style="transform-origin:0px 0px">{trunk}{wood}{"".join(layers)}{blossoms}</g></g>')


# ---------------------------------------------------------------------------
# Котики
# ---------------------------------------------------------------------------


def _cat_head(eyes: str, body: str, patch: str | None) -> str:
    patch_svg = f'<ellipse cx="-10" cy="-72" rx="11" ry="8" fill="{patch}"/>' if patch else ""
    return (
        f'<path d="M-22,-70 L-20,-96 L-3,-80 Z M22,-70 L20,-96 L3,-80 Z" fill="{body}" stroke="{OUTLINE}" '
        f'stroke-width="2.2" stroke-linejoin="round"/>'
        f'<path d="M-18,-75 L-17,-89 L-8,-81 Z M18,-75 L17,-89 L8,-81 Z" fill="#ffb3c7"/>'
        f'<ellipse cx="0" cy="-60" rx="27" ry="22" fill="{body}"/>{patch_svg}'
        f'<ellipse cx="0" cy="-60" rx="27" ry="22" fill="none" stroke="{OUTLINE}" stroke-width="2.2"/>'
        f'{eyes}'
        f'<ellipse cx="-16" cy="-53" rx="5" ry="3" fill="#ffb3c7" opacity=".85"/>'
        f'<ellipse cx="16" cy="-53" rx="5" ry="3" fill="#ffb3c7" opacity=".85"/>'
        f'<path d="M-2.5,-57 L2.5,-57 L0,-54 Z" fill="#ff8fa8"/>'
        f'<path d="M-5,-52 q2.5,3 5,0 q2.5,3 5,0" stroke="{OUTLINE}" stroke-width="1.6" fill="none" '
        f'stroke-linecap="round"/>'
        f'<path d="M-21,-57 L-34,-59 M-21,-53 L-33,-50 M21,-57 L34,-59 M21,-53 L33,-50" stroke="{OUTLINE}" '
        f'stroke-width="1.1" opacity=".6"/>'
    )


OPEN_EYES = ('<g class="blink"><ellipse cx="-9" cy="-61" rx="3.2" ry="4.2" fill="#3b2a2a"/>'
             '<ellipse cx="9" cy="-61" rx="3.2" ry="4.2" fill="#3b2a2a"/></g>'
             '<circle cx="-8" cy="-63" r="1.2" fill="#fff"/><circle cx="10" cy="-63" r="1.2" fill="#fff"/>')
HAPPY_EYES = (f'<path d="M-14,-60 q5,-6 10,0 M4,-60 q5,-6 10,0" stroke="{OUTLINE}" stroke-width="2.2" '
              f'fill="none" stroke-linecap="round"/>')


def cat_sitting(x: float, y: float, scale: float = 1.0, body: str = "#fffaf3",
                patch: str | None = "#f6a25e", tail_patch: str | None = "#6b5048") -> str:
    """Сидящий котик анфас; хвост виляет, глазки моргают."""
    tail_color = tail_patch or body
    return f"""
<g transform="translate({x},{y}) scale({scale})">
  <g><animateTransform attributeName="transform" type="rotate" values="-6 18 -6; 14 18 -6; -6 18 -6"
       dur="2.8s" repeatCount="indefinite"/>
    <path d="M18,-6 C42,-4 48,-26 36,-42" stroke="{OUTLINE}" stroke-width="12" fill="none" stroke-linecap="round"/>
    <path d="M18,-6 C42,-4 48,-26 36,-42" stroke="{tail_color}" stroke-width="7.5" fill="none" stroke-linecap="round"/>
  </g>
  <path d="M-24,0 C-28,-22 -20,-44 0,-46 C20,-44 28,-22 24,0 Z" fill="{body}" stroke="{OUTLINE}" stroke-width="2.2"/>
  <ellipse cx="0" cy="-20" rx="11" ry="14" fill="#ffffff" opacity=".8"/>
  <ellipse cx="-9" cy="-2" rx="7.5" ry="5" fill="{body}" stroke="{OUTLINE}" stroke-width="2"/>
  <ellipse cx="9" cy="-2" rx="7.5" ry="5" fill="{body}" stroke="{OUTLINE}" stroke-width="2"/>
  {_cat_head(OPEN_EYES, body, patch)}
</g>"""


def maneki_neko(x: float, y: float, scale: float = 1.0) -> str:
    """Манэки-нэко: котик-талисман машет лапкой «пока-пока»."""
    body = "#fffdf8"
    return f"""
<g transform="translate({x},{y}) scale({scale})">
  <path d="M-24,0 C-28,-22 -20,-44 0,-46 C20,-44 28,-22 24,0 Z" fill="{body}" stroke="{OUTLINE}" stroke-width="2.2"/>
  <ellipse cx="-12" cy="-26" rx="8" ry="6" fill="#f6a25e" opacity=".9"/>
  <ellipse cx="-9" cy="-2" rx="7.5" ry="5" fill="{body}" stroke="{OUTLINE}" stroke-width="2"/>
  <g><animateTransform attributeName="transform" type="rotate" values="-12 16 -40; 18 16 -40; -12 16 -40"
       dur="1.1s" repeatCount="indefinite"/>
    <path d="M14,-38 C16,-52 20,-62 26,-66" stroke="{OUTLINE}" stroke-width="13" fill="none" stroke-linecap="round"/>
    <path d="M14,-38 C16,-52 20,-62 26,-66" stroke="{body}" stroke-width="9" fill="none" stroke-linecap="round"/>
    <circle cx="27" cy="-68" r="2" fill="#ffb3c7"/>
  </g>
  {_cat_head(HAPPY_EYES, body, "#f6a25e")}
  <path d="M-20,-42 Q0,-34 20,-42" stroke="#e53950" stroke-width="5" fill="none" stroke-linecap="round"/>
  <circle cx="0" cy="-36" r="4.5" fill="#ffc83d" stroke="#c98a00" stroke-width="1.2"/>
</g>"""


def cat_sleeping(x: float, y: float, scale: float = 1.0, body: str = "#cfcfd6") -> str:
    """Спящий клубочком котик с «zzZ»."""
    return f"""
<g transform="translate({x},{y}) scale({scale})">
  <ellipse cx="0" cy="-16" rx="40" ry="18" fill="{body}" stroke="{OUTLINE}" stroke-width="2.2"/>
  <path d="M34,-8 C40,4 10,8 -26,2" stroke="{OUTLINE}" stroke-width="11" fill="none" stroke-linecap="round"/>
  <path d="M34,-8 C40,4 10,8 -26,2" stroke="{body}" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M-38,-26 L-36,-46 L-26,-34 Z M-18,-30 L-12,-48 L-6,-32 Z" fill="{body}" stroke="{OUTLINE}"
        stroke-width="2" stroke-linejoin="round"/>
  <ellipse cx="-22" cy="-22" rx="20" ry="14" fill="{body}" stroke="{OUTLINE}" stroke-width="2.2"/>
  <path d="M-31,-22 q4,3 8,0 M-19,-22 q4,3 8,0" stroke="{OUTLINE}" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <ellipse cx="-33" cy="-16" rx="3.5" ry="2" fill="#ffb3c7"/>
  <g font-weight="800" fill="{t.ACCENT_2}">
    <text class="zzz" x="-6" y="-44" font-size="13">z</text>
    <text class="zzz" x="-6" y="-44" font-size="16" style="animation-delay:1.2s">z</text>
    <text class="zzz" x="-6" y="-44" font-size="19" style="animation-delay:2.4s">Z</text>
  </g>
</g>"""


def cat_peek(x: float, y: float, scale: float = 1.0, body: str = "#f9c98f") -> tuple[str, str]:
    """Котик выглядывает из-за верхнего края карточки: (голова — рисовать ДО карточки, лапки — ПОСЛЕ)."""
    head = f"""
<g transform="translate({x},{y + 6 + 38 * scale}) scale({scale})">
  <g><animateTransform attributeName="transform" type="translate" values="0 6; 0 0; 0 0; 0 6"
       keyTimes="0; .15; .85; 1" dur="7s" repeatCount="indefinite"/>
  {_cat_head(OPEN_EYES, body, "#e88a3c")}
  </g>
</g>"""
    paws = f"""
<g transform="translate({x},{y}) scale({scale})">
  <ellipse cx="-13" cy="1" rx="9" ry="6" fill="{body}" stroke="{OUTLINE}" stroke-width="2"/>
  <ellipse cx="13" cy="1" rx="9" ry="6" fill="{body}" stroke="{OUTLINE}" stroke-width="2"/>
  <path d="M-16,3 v-3 M-11,3 v-3 M10,3 v-3 M15,3 v-3" stroke="{OUTLINE}" stroke-width="1.2"/>
</g>"""
    return head, paws


# ---------------------------------------------------------------------------
# Пруд и карпы кои
# ---------------------------------------------------------------------------

_KOI_BODY = "M34,0 C30,-10 14,-14 0,-12 C-14,-10 -24,-6 -30,0 C-24,6 -14,10 0,12 C14,14 30,10 34,0 Z"
_KOI_TAIL = "M-28,0 C-38,-4 -46,-14 -54,-17 C-48,-6 -48,6 -54,17 C-46,14 -38,4 -28,0 Z"
_KOI_FIN = "M14,-10 C10,-22 0,-25 -4,-22 C0,-17 7,-13 14,-10 Z"

KOI_STYLES = {
    "kohaku": ("#fffaf5", '<ellipse cx="18" cy="-1" rx="13" ry="9" fill="#ff5a36"/>'
                          '<ellipse cx="-10" cy="3" rx="11" ry="7" fill="#ff5a36"/>'),
    "sanke": ("#fffaf5", '<ellipse cx="14" cy="2" rx="12" ry="8" fill="#ff5a36"/>'
                         '<ellipse cx="-14" cy="-3" rx="8" ry="6" fill="#ff5a36"/>'
                         '<circle cx="2" cy="-6" r="3" fill="#2b2b2b"/><circle cx="-6" cy="6" r="2.4" fill="#2b2b2b"/>'),
    "ogon": ("#ffc94a", '<ellipse cx="6" cy="0" rx="22" ry="4" fill="#fff1b0" opacity=".8"/>'),
    "chagoi": ("#ff8a3d", '<ellipse cx="22" cy="0" rx="10" ry="9" fill="#fff4e6"/>'),
}


def koi(style: str, path: str, dur: float, scale: float = 1.0, begin: float = 0.0) -> str:
    """Карп кои плывёт по замкнутому пути и разворачивается по ходу движения."""
    body, pattern = KOI_STYLES[style]
    return f"""
<g><animateMotion dur="{dur}s" begin="{-begin}s" repeatCount="indefinite" rotate="auto" path="{path}"/>
  <g transform="scale({scale})">
    <path d="{_KOI_BODY}" transform="translate(5,7)" fill="#1d5f86" opacity=".18"/>
    <g><animateTransform attributeName="transform" type="rotate" values="-16 -28 0; 16 -28 0; -16 -28 0"
         dur="1s" repeatCount="indefinite"/>
      <path d="{_KOI_TAIL}" fill="{body}" opacity=".9"/>
    </g>
    <path d="{_KOI_FIN}" fill="#ffffff" opacity=".7"/>
    <path d="{_KOI_FIN}" transform="scale(1,-1)" fill="#ffffff" opacity=".7"/>
    <path d="{_KOI_BODY}" fill="{body}"/>
    <g clip-path="url(#koiBody)">{pattern}</g>
    <circle cx="28" cy="-5" r="1.6" fill="#1b1b1b"/><circle cx="28" cy="5" r="1.6" fill="#1b1b1b"/>
  </g>
</g>"""


def lily_pad(x: float, y: float, r: float, rot: float = 0, lotus: bool = False) -> str:
    a1, a2 = math.radians(-10), math.radians(10)
    d = (f"M0,0 L{r * math.cos(a1):.1f},{r * math.sin(a1):.1f} "
         f"A{r},{r} 0 1 0 {r * math.cos(a2):.1f},{r * math.sin(a2):.1f} Z")
    veins = "".join(f'<path d="M0,0 L{r * .85 * math.cos(math.radians(a)):.1f},{r * .85 * math.sin(math.radians(a)):.1f}" '
                    f'stroke="#9be08a" stroke-width="1" opacity=".7"/>' for a in range(40, 360, 55))
    flower_svg = ""
    if lotus:
        petals = "".join(f'<ellipse cx="0" cy="-9" rx="5" ry="10" fill="#ffc2dc" stroke="#ff8fc7" stroke-width=".8" '
                         f'transform="rotate({a})"/>' for a in range(0, 360, 45))
        flower_svg = f'<g>{petals}<circle r="5" fill="#ffe27a"/></g>'
    return (f'<g transform="translate({x},{y}) rotate({rot})"><g class="float">'
            f'<path d="{d}" transform="translate(3,4)" fill="#1d5f86" opacity=".2"/>'
            f'<path d="{d}" fill="#6cc070" stroke="#4fa85a" stroke-width="1.5"/>{veins}{flower_svg}</g></g>')


def ripples(rng: random.Random, spots) -> str:
    return "".join(
        f'<ellipse class="ripple" cx="{x}" cy="{y}" rx="34" ry="14" fill="none" stroke="#ffffff" stroke-width="1.6" '
        f'style="animation-duration:{rng.uniform(3.5, 5.5):.1f}s;animation-delay:{-rng.uniform(0, 5):.1f}s"/>'
        for x, y in spots
    )


def floating_petals(rng: random.Random, count: int, width: float, height: float) -> str:
    return "".join(
        f'<g transform="translate({rng.uniform(10, width - 10):.0f},{rng.uniform(10, height - 10):.0f}) '
        f'rotate({rng.uniform(0, 360):.0f})"><g class="float" style="animation-duration:{rng.uniform(5, 9):.1f}s;'
        f'animation-delay:{-rng.uniform(0, 8):.1f}s"><path d="{PETAL_PATH}" fill="#ffc2dc" '
        f'transform="scale({rng.uniform(.45, .7):.2f})"/></g></g>'
        for _ in range(count)
    )
