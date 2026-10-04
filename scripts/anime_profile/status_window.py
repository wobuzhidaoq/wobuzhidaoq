"""«Окно статуса» в стиле исекай-аниме: уровень, ранг гильдии, характеристики и навыки."""

import datetime as dt
import math
import random

from . import art
from . import theme as t
from .fonts import FontEmbedder
from .scenery import CARD_DEFS, glass, meadow_card
from .svg import PETAL_GRADIENT, document, esc, petal_css, truncate

CLASSES = {
    "Python": "Serpent Summoner",
    "JavaScript": "JS Illusionist",
    "TypeScript": "Knight of Strict Types",
    "Java": "Coffee Alchemist",
    "Kotlin": "Kotlin Samurai",
    "C": "Lord of Memory",
    "C++": "Pointer Necromancer",
    "C#": ".NET Paladin",
    "Go": "Gopher Ninja",
    "Rust": "Crab Blacksmith",
    "Ruby": "Ruby Mage",
    "PHP": "Elephant Elder",
    "Swift": "Swallow Scout",
    "Dart": "Dart Thrower",
    "Lua": "Moon Mage",
    "Shell": "Terminal Shaman",
    "PowerShell": "Terminal Shaman",
    "HTML": "Markup Architect",
    "CSS": "Style Master",
    "SCSS": "Style Master",
    "Vue": "Component Summoner",
    "Svelte": "Component Summoner",
    "Jupyter Notebook": "Data Oracle",
    "R": "Data Oracle",
    "Haskell": "Lambda Temple Monk",
    "Elixir": "Elixir Alchemist",
    "Assembly": "Ancient Rune Scribe",
    "GDScript": "World Maker",
    "React": "Component Summoner",
    "Tailwind CSS": "Style Master",
}

# (условие, титул) — берётся первый подходящий.
TITLES = [
    (lambda s: s["streak_longest"] >= 100, "Immortal Streak"),
    (lambda s: s["contributions_year"] >= 2000, "Commit Overlord"),
    (lambda s: s["stars"] >= 100, "Star Wanderer"),
    (lambda s: s["streak_longest"] >= 30, "The Tireless"),
    (lambda s: s["contributions_year"] >= 500, "Code Samurai"),
    (lambda s: s["followers"] >= 50, "Guild Senpai"),
    (lambda s: s["prs_total"] >= 20, "Pull Request Master"),
    (lambda s: s["public_repos"] >= 10, "Repo Collector"),
    (lambda s: s["contributions_year"] >= 100, "Promising Rookie"),
    (lambda s: True, "Rookie from the Starting Village"),
]

RANKS = [(5, "F"), (10, "E"), (15, "D"), (22, "C"), (30, "B"), (40, "A"), (55, "S"), (75, "SS")]


def _fmt(n: int) -> str:
    return f"{n:,}"


def compute(stats: dict, derived: dict, cfg: dict) -> dict:
    s = {**stats, **derived}
    xp = (s["contributions_year"] + s["stars"] * 10 + s["followers"] * 5
          + s["public_repos"] * 5 + s["prs_total"] * 3)
    level = 1 + int(math.sqrt(xp / 5))
    floor_xp, next_xp = 5 * (level - 1) ** 2, 5 * level ** 2
    rank = next((r for limit, r in RANKS if level < limit), "SSS")
    declared = cfg.get("skills") or []
    top_lang = declared[0]["name"] if declared else (s["languages"][0]["name"] if s["languages"] else None)
    return {
        "xp": xp,
        "level": level,
        "xp_into": xp - floor_xp,
        "xp_span": next_xp - floor_xp,
        "rank": rank,
        "class": cfg.get("class") or CLASSES.get(top_lang, "Wandering Coder"),
        "title": cfg.get("title") or next(title for cond, title in TITLES if cond(s)),
        "race": cfg.get("race", "Human (?)"),
        "guild_year": s["created_at"][:4],
    }


def skill_rows(stats: dict, cfg: dict, exclude: list | None = None) -> list[dict]:
    """Строки «Навыков»: твой стек из config (с уровнями) или, если его нет, языки из GitHub."""
    declared = cfg.get("skills") or []
    if declared:
        return [{"name": d["name"], "color": d["color"], "ratio": d["power"], "label": d["level"],
                 "group": d["group"]} for d in declared[:6]]
    langs = [lang for lang in stats["languages"] if lang["name"] not in (exclude or [])][:5]
    total = sum(lang["size"] for lang in stats["languages"] if lang["name"] not in (exclude or [])) or 1
    top = langs[0]["size"] / total if langs else 1
    return [{"name": lang["name"], "color": lang.get("color") or t.LILAC, "ratio": lang["size"] / total / top,
             "label": f"{lang['size'] / total * 100:.1f}%", "group": i} for i, lang in enumerate(langs)]


def build(stats: dict, derived: dict, cfg: dict, fonts: FontEmbedder,
          exclude_languages: list[str] | None = None, now: dt.datetime | None = None) -> str:
    top = 58  # место над карточкой для котика, который выглядывает сверху
    w, h = 900, 628
    rng = random.Random(5)
    now = now or dt.datetime.now(dt.timezone.utc)
    info = compute(stats, derived, cfg)

    skills = skill_rows(stats, cfg, exclude_languages)

    texts: list[str] = []  # всё, что попадёт на картинку, — для сабсета шрифта

    def text(x, y, value, size=13, weight=500, fill=t.INK, anchor="start", extra=""):
        value = str(value)
        texts.append(value)
        return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
                f'text-anchor="{anchor}" {extra}>{esc(value)}</text>')

    parts: list[str] = [glass(20, 20, 860, 508)]

    # --- шапка окна ---
    parts.append(f'<rect x="34" y="37" width="10" height="10" fill="{t.SKY}" transform="rotate(45 39 42)"/>')
    parts.append(text(54, 48, "STATUS", 15, 800, t.ACCENT_2, extra='letter-spacing="5"'))
    parts.append(text(140, 48, "ステータス", 15, 800, t.ACCENT, extra='letter-spacing="2"'))
    parts.append(text(864, 47, f"Updated: {now:%b %d, %Y · %H:%M} UTC", 12, 500, t.INK_SOFT, "end"))
    parts.append('<rect x="36" y="64" width="828" height="2" rx="1" fill="url(#hline)"/>')

    # --- левая колонка: персонаж ---
    parts.append(text(36, 110, truncate(stats["name"], 16), 30, 800, t.INK))
    texts.append(f"@{stats['login']} · Guild rank {info['rank']}")
    parts.append(
        f'<text x="36" y="137" font-size="14" font-weight="500" fill="{t.INK_SOFT}">'
        f'@{esc(stats["login"])} · Guild rank '
        f'<tspan fill="{t.GOLD}" font-weight="800" font-size="17">{info["rank"]}</tspan></text>'
    )
    parts.append(f'<rect x="338" y="82" width="92" height="64" rx="14" fill="#ffffff" '
                 f'stroke="{t.ACCENT}" stroke-width="2" class="pulse"/>')
    parts.append(text(384, 103, "LV", 11, 800, t.ACCENT_2, "middle", 'letter-spacing="3"'))
    parts.append(text(384, 136, info["level"], 30, 800, t.ACCENT, "middle"))

    rows = [
        ("Class", info["class"]),
        ("Title", f"“{info['title']}”"),
        ("Race", info["race"]),
        ("Guild", f"GitHub · since {info['guild_year']}"),
    ]
    for i, (label, value) in enumerate(rows):
        y = 180 + i * 26
        parts.append(text(36, y, label, 13, 500, t.INK_SOFT))
        parts.append(text(118, y, truncate(value, 34), 14, 800 if i < 2 else 500, t.INK))

    bars = [
        ("EXP", "experience to next level", info["xp_into"], info["xp_span"],
         f"{_fmt(info['xp_into'])} / {_fmt(info['xp_span'])}", "url(#gExp)", t.ACCENT),
        ("HP", "commit streak", derived["streak_current"], max(derived["streak_longest"], 1),
         f"{derived['streak_current']} days · best {derived['streak_longest']}", "url(#gHp)", "#e8456b"),
        ("MP", "active days out of 30", derived["active_days_30"], 30,
         f"{derived['active_days_30']} / 30", "url(#gMp)", t.ACCENT_2),
    ]
    for i, (tag, desc, value, maximum, label, grad, color) in enumerate(bars):
        y = 302 + i * 50
        ratio = max(0.0, min(1.0, value / maximum)) if maximum else 0.0
        parts.append(text(36, y, tag, 12, 800, color, extra='letter-spacing="2"'))
        parts.append(text(36 + len(tag) * 9 + 10, y, desc, 12, 500, t.INK_SOFT))
        parts.append(text(430, y, label, 12, 800, t.INK, "end"))
        parts.append(f'<rect x="36" y="{y + 9}" width="394" height="10" rx="5" fill="{t.TRACK}"/>')
        if ratio > 0:
            parts.append(f'<rect class="grow" style="animation-delay:{0.2 + i * 0.25:.2f}s" x="36" y="{y + 9}" '
                         f'width="{max(394 * ratio, 6):.1f}" height="10" rx="5" fill="{grad}"/>')

    # --- правая колонка: характеристики ---
    parts.append(text(470, 100, "能力値 · Attributes", 13, 800, t.ACCENT_2, extra='letter-spacing="2"'))
    cells = [
        ("STR", "commits this year", stats["commits_year"]),
        ("INT", "pull requests", stats["prs_total"]),
        ("DEX", "issues", stats["issues_total"]),
        ("VIT", "best streak, days", derived["streak_longest"]),
        ("CHA", "followers", stats["followers"]),
        ("LUK", "stars", stats["stars"]),
    ]
    for i, (abbr, desc, value) in enumerate(cells):
        x, y = 470 + (i % 2) * 204, 114 + (i // 2) * 66
        parts.append(f'<rect x="{x}" y="{y}" width="190" height="56" rx="12" fill="{t.CELL}" '
                     f'stroke="{t.CELL_STROKE}" stroke-width="1.5"/>')
        parts.append(text(x + 14, y + 23, abbr, 12, 800, t.ACCENT, extra='letter-spacing="2"'))
        parts.append(text(x + 14, y + 42, desc, 11, 500, t.INK_SOFT))
        parts.append(text(x + 176, y + 38, _fmt(value), 24, 800, t.INK, "end"))

    # --- навыки (языки) ---
    parts.append(text(470, 334, "スキル · Skills", 13, 800, t.ACCENT_2, extra='letter-spacing="2"'))
    if skills:
        step = 22 if len(skills) <= 5 else 19
        for i, sk in enumerate(skills):
            y = 358 + i * step
            color = sk["color"]
            parts.append(f'<circle cx="476" cy="{y - 4}" r="5" fill="{color}" stroke="#ffffff" stroke-width="1"/>')
            parts.append(text(488, y, truncate(sk["name"], 15), 13, 500, t.INK))
            parts.append(f'<rect x="616" y="{y - 8}" width="196" height="6" rx="3" fill="{t.TRACK}"/>')
            parts.append(f'<rect class="grow" style="animation-delay:{0.4 + i * 0.12:.2f}s" x="616" y="{y - 8}" '
                         f'width="{max(196 * sk["ratio"], 4):.1f}" height="6" rx="3" fill="{color}"/>')
            parts.append(text(864, y, sk["label"], 12, 500, t.INK_SOFT, "end"))
    else:
        parts.append(text(470, 366, "Skills not revealed yet… (・_・;)", 14, 500, t.INK_SOFT))

    # --- нижняя полоса: снаряжение и журнал ---
    parts.append('<rect x="36" y="466" width="828" height="1.5" fill="url(#hline)" opacity=".7"/>')
    parts.append(text(36, 490, "装備 · Equipment", 12, 800, t.ACCENT_2, extra='letter-spacing="2"'))
    equipment = " · ".join(cfg.get("equipment", [])) or "Just a stick and a pot lid for now"
    parts.append(text(36, 514, truncate(equipment, 82), 13, 500, t.INK))

    weekly = derived["weekly"] or [0]
    journal = f"Adventure log · {len(weekly)} wks" if derived["weekly"] else "Adventure log"
    parts.append(text(864, 490, journal, 12, 800, t.ACCENT_2, "end", 'letter-spacing="1"'))
    peak = max(weekly) or 1
    bar_w, gap = 6, 2.2
    start_x = 864 - len(weekly) * (bar_w + gap) + gap
    for i, v in enumerate(weekly):
        bh = max(2.0, 24 * v / peak)
        parts.append(f'<rect class="growY" style="animation-delay:{0.5 + i * 0.03:.2f}s" '
                     f'x="{start_x + i * (bar_w + gap):.1f}" y="{522 - bh:.1f}" width="{bar_w}" '
                     f'height="{bh:.1f}" rx="2" fill="url(#gExp)" opacity="{0.5 + 0.5 * v / peak:.2f}"/>')

    defs = f"""
{art.ART_DEFS}
{CARD_DEFS}
<linearGradient id="gExp" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset="1" stop-color="{t.LILAC}"/></linearGradient>
<linearGradient id="gHp" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#ff6b8b"/><stop offset="1" stop-color="{t.PINK}"/></linearGradient>
<linearGradient id="gMp" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.SKY}"/><stop offset="1" stop-color="{t.LILAC}"/></linearGradient>
{PETAL_GRADIENT}
"""
    css = art.ART_CSS + petal_css(h + 40, -120) + """
.grow { animation: grow 1.6s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: left center; }
@keyframes grow { from { transform: scaleX(0); } }
.growY { animation: growY 1.2s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: center bottom; }
@keyframes growY { from { transform: scaleY(0); } }
.pulse { animation: pulse 2.6s ease-in-out infinite alternate; }
@keyframes pulse { from { stroke-opacity: .45; } to { stroke-opacity: 1; } }
.blinkT { animation: blinkT 1.2s steps(2, start) infinite; }
@keyframes blinkT { to { visibility: hidden; } }
"""
    cat_head, cat_paws = art.cat_peek(780, top + 8, 1.1)
    body = f"""
{cat_head}
{meadow_card(rng, w, h, top=top)}
<g transform="translate(0,{top})">
{''.join(parts)}
<rect class="blinkT" x="232" y="35" width="7" height="15" rx="1.5" fill="{t.ACCENT}"/>
</g>
{cat_paws}
"""
    font_css = fonts.css("".join(texts) + "0123456789", (500, 800))
    return document(w, h, f"Status: {stats['name']} — Lv. {info['level']}", defs, css, body, font_css)
