"""Карточка «Цитата дня»: пруд с карпами кои, а цитата — на бумажке, плавающей по воде."""

import datetime as dt
import random

from . import art
from . import theme as t
from .fonts import FontEmbedder
from .scenery import CARD_DEFS
from .svg import PETAL_GRADIENT, document, esc, flower, wrap


def pick(quotes: list[dict], day: dt.date) -> tuple[int, dict]:
    # Каждый «круг» из len(quotes) дней показывает все цитаты по разу, в перемешанном порядке.
    cycle, pos = divmod(day.toordinal(), len(quotes))
    order = list(range(len(quotes)))
    random.Random(cycle).shuffle(order)
    return order[pos], quotes[order[pos]]


def build(quotes: list[dict], fonts: FontEmbedder, day: dt.date | None = None) -> str:
    day = day or dt.datetime.now(dt.timezone.utc).date()
    _, q = pick(quotes, day)
    lines = wrap(q["text"], 50, 4)
    line_h = 32
    w = 900
    px, py, pw = 96, 30, 708
    ph = max(84 + len(lines) * line_h + 40, 196)
    h = ph + 60
    cy = h / 2
    rng = random.Random(day.toordinal())

    caption = f"Цитата дня · {day:%d.%m.%Y}"
    author = f"— {q['who']} · «{q['anime']}»"
    vertical = "今日の名言"

    text_lines = "".join(
        f'<text x="{px + 56}" y="{py + 84 + i * line_h}" font-size="22" font-weight="800" fill="{t.INK}">'
        f"{esc(line)}</text>"
        for i, line in enumerate(lines)
    )
    vertical_text = "".join(
        f'<text x="{px + pw - 34}" y="{py + 40 + i * 24}" font-size="19" font-weight="800" fill="{t.ACCENT}" '
        f'text-anchor="middle">{ch}</text>'
        for i, ch in enumerate(vertical)
    )
    author_y = py + 84 + len(lines) * line_h + 10

    big = f"M40,{cy} A410,{cy - 16} 0 1 1 860,{cy} A410,{cy - 16} 0 1 1 40,{cy} Z"
    small = f"M70,{cy} A380,{cy - 30} 0 1 0 830,{cy} A380,{cy - 30} 0 1 0 70,{cy} Z"
    corner = f"M30,{h - 40} C40,{h - 90} 120,{h - 90} 140,{h - 50} C150,{h - 20} 60,{h - 10} 30,{h - 40} Z"

    defs = f"""
<clipPath id="card"><rect x="8" y="8" width="{w - 16}" height="{h - 16}" rx="22"/></clipPath>
{art.ART_DEFS}
{CARD_DEFS}
{PETAL_GRADIENT}
<filter id="paperShadow" x="-5%" y="-10%" width="110%" height="130%">
  <feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#1d5f86" flood-opacity=".25"/>
</filter>
"""
    css = art.ART_CSS + """
.rise { animation: rise 1.4s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
.bob { animation: bob 6s ease-in-out infinite alternate; }
@keyframes bob { from { transform: translateY(-2px) rotate(-.3deg); } to { transform: translateY(2px) rotate(.3deg); } }
"""
    body = f"""
<g clip-path="url(#card)">
  <rect x="8" y="8" width="{w - 16}" height="{h - 16}" fill="url(#water)"/>
  {art.ripples(rng, [(160, 40), (760, h - 30), (450, h - 18), (870, 70), (30, cy)])}
  {art.koi("kohaku", big, 26, .85)}
  {art.koi("ogon", big, 26, .7, 13)}
  {art.koi("sanke", small, 31, .8, 6)}
  {art.koi("chagoi", corner, 12, .55)}
  {art.floating_petals(rng, 14, w, h)}
  {art.lily_pad(58, 44, 28, 20, lotus=True)}{art.lily_pad(845, h - 42, 32, 200)}
  {art.lily_pad(860, 36, 18, 120)}{art.lily_pad(48, h - 34, 20, 300)}
</g>
<rect x="8" y="8" width="{w - 16}" height="{h - 16}" rx="22" fill="none" stroke="url(#border)" stroke-width="2"/>
<g class="bob">
  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="#fffdf8" fill-opacity=".92"
        stroke="#ffd6e8" stroke-width="2" filter="url(#paperShadow)"/>
  <rect x="{px + pw - 54}" y="{py + 18}" width="1.5" height="{len(vertical) * 24 + 4}" fill="{t.PINK}" opacity=".6"/>
  {vertical_text}
  {flower(px + pw - 34, py + ph - 24, .75)}
  <g class="rise">
    <text x="{px - 14}" y="{py + 80}" font-size="56" font-weight="800" fill="{t.PINK}">「</text>
    <text x="{px + 56}" y="{py + 42}" font-size="13" font-weight="800" fill="{t.ACCENT_2}"
          letter-spacing="3">{esc(caption)}</text>
    {text_lines}
    <text x="{px + 56}" y="{author_y + 18}" font-size="15" font-weight="800" fill="{t.ACCENT}">{esc(author)}</text>
  </g>
</g>
"""
    all_text = caption + author + vertical + "「" + "".join(lines)
    font_css = fonts.css(all_text, (800,))
    return document(w, h, f"Цитата дня: {q['text']} {author}", defs, css, body, font_css)
