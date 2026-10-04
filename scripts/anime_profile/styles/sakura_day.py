"""☀️ Дневная сакура: небо, облака, зелёный холм, котики, пруд с карпами кои."""

import random

from .. import anime_list, art, quote as quote_card, scenery, status_window
from .. import theme as t
from ..svg import PETAL_GRADIENT, balanced_wrap, document, esc, flower, speech_bubble


def header(cfg, ctx):
    return scenery.build_header(cfg, ctx.fonts)


def divider(ctx):
    return scenery.build_divider()


def footer(cfg, ctx):
    return scenery.build_footer(cfg, ctx.fonts)


def status(stats, derived, cfg, ctx, exclude):
    return status_window.build(stats, derived, cfg, ctx.fonts, exclude)


def quote(quotes, ctx, pinned=False):
    return quote_card.build(quotes, ctx.fonts, pinned=pinned)


def anime(data, username, ctx, max_items):
    return anime_list.build(data, username, ctx.fonts, max_items)


def views_caption(cfg, ctx):
    """Подпись к счётчику: облачко на светлой карточке, хвостик указывает на девочек слева."""
    rng = random.Random(13)
    w, h = 400, 130
    caption = cfg.get("caption", "")
    tab = cfg.get("tab", "")
    lines = balanced_wrap(caption, 22, 2)
    cx, cy = 226, 70
    text = "".join(f'<text x="{cx}" y="{cy - (len(lines) - 1) * 12 + 7 + i * 24}" font-size="19" '
                   f'font-weight="800" fill="{t.INK}" text-anchor="middle">{esc(line)}</text>'
                   for i, line in enumerate(lines))
    body = f"""
<clipPath id="vc"><rect x="30" y="8" width="362" height="114" rx="18"/></clipPath>
<g clip-path="url(#vc)">
  <rect x="30" y="8" width="362" height="114" fill="url(#skySoft)"/>
  {art.cloud(110, 104, .32, 40)}{art.cloud(330, 30, .28, 50)}
  {art.sparkles(rng, [(370, 100, .6), (60, 40, .5)], "#ffb000")}
</g>
<rect x="30" y="8" width="362" height="114" rx="18" fill="none" stroke="url(#border)" stroke-width="2"/>
<rect x="46" y="13" width="98" height="25" rx="12.5" fill="{t.ACCENT}"/>
<text x="95" y="31" font-size="15" font-weight="800" fill="#fff" text-anchor="middle">{esc(tab)}</text>
{flower(372, 30, .7)}
<g class="pop">{speech_bubble(cx, cy, 150, 44, 4, 98, t.PINK, 2.5)}{text}</g>
"""
    css = art.ART_CSS + """
.pop { animation: pop .7s cubic-bezier(.2,1.5,.4,1) .3s both; transform-box: fill-box; transform-origin: center; }
@keyframes pop { from { transform: scale(.2); opacity: 0; } to { transform: scale(1); opacity: 1; } }
"""
    defs = art.ART_DEFS + scenery.CARD_DEFS + PETAL_GRADIENT
    return document(w, h, caption, defs, css, body, ctx.fonts.css(caption + tab, (800,)))
