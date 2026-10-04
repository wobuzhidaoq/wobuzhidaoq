"""Карточка «Цитата дня»: каждый день новая цитата из data/quotes.json."""

import datetime as dt
import random

from . import theme as t
from .fonts import FontEmbedder
from .svg import PETAL_GRADIENT, document, esc, falling_petals, flower, petal_css, wrap


def pick(quotes: list[dict], day: dt.date) -> tuple[int, dict]:
    # Каждый «круг» из len(quotes) дней показывает все цитаты по разу, в перемешанном порядке.
    cycle, pos = divmod(day.toordinal(), len(quotes))
    order = list(range(len(quotes)))
    random.Random(cycle).shuffle(order)
    return order[pos], quotes[order[pos]]


def build(quotes: list[dict], fonts: FontEmbedder, day: dt.date | None = None) -> str:
    day = day or dt.datetime.now(dt.timezone.utc).date()
    _, q = pick(quotes, day)
    lines = wrap(q["text"], 54, 4)
    line_h = 32
    w = 900
    h = max(150 + len(lines) * line_h, 230)
    rng = random.Random(day.toordinal())

    caption = f"Цитата дня · {day:%d.%m.%Y}"
    author = f"— {q['who']} · «{q['anime']}»"
    vertical = "今日の名言"

    text_lines = "".join(
        f'<text x="96" y="{100 + i * line_h}" font-size="22" font-weight="500" fill="{t.TEXT}">{esc(line)}</text>'
        for i, line in enumerate(lines)
    )
    vertical_text = "".join(
        f'<text x="846" y="{58 + i * 26}" font-size="20" font-weight="800" fill="{t.PINK}" '
        f'text-anchor="middle" opacity=".85">{ch}</text>'
        for i, ch in enumerate(vertical)
    )
    author_y = 100 + len(lines) * line_h + 10

    defs = f"""
<clipPath id="card"><rect x="8" y="8" width="{w - 16}" height="{h - 16}" rx="20"/></clipPath>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#1a1140"/><stop offset="1" stop-color="#0d0a24"/></linearGradient>
<linearGradient id="border" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset="1" stop-color="{t.LAVENDER}"/></linearGradient>
{PETAL_GRADIENT}
"""
    css = petal_css(h + 40, -100) + """
.rise { animation: rise 1.4s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
.rot { animation: rot 20s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes rot { to { transform: rotate(360deg); } }
"""
    body = f"""
<rect x="8" y="8" width="{w - 16}" height="{h - 16}" rx="20" fill="url(#bg)" stroke="url(#border)" stroke-width="1.5"/>
<g clip-path="url(#card)">
  {falling_petals(rng, 7, w, h, 0.4, 0.7, 0.45)}
  <g class="rot" opacity=".9">{flower(846, h - 40, 1.1, 0)}</g>
</g>
<rect x="808" y="30" width="1.5" height="{len(vertical) * 26 + 10}" fill="{t.PINK}" opacity=".4"/>
{vertical_text}
<g class="rise">
  <text x="14" y="112" font-size="64" font-weight="800" fill="{t.PINK}" opacity=".85">「</text>
  <text x="96" y="52" font-size="13" font-weight="700" fill="{t.CYAN}" letter-spacing="3">{esc(caption)}</text>
  {text_lines}
  <text x="96" y="{author_y + 18}" font-size="15" font-weight="700" fill="{t.PINK_LIGHT}">{esc(author)}</text>
</g>
"""
    all_text = caption + author + vertical + "「" + "".join(lines)
    font_css = fonts.css(all_text, (500, 700, 800))
    return document(w, h, f"Цитата дня: {q['text']} {author}", defs, css, body, font_css)
