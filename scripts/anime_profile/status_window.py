"""«Окно статуса» в стиле исекай-аниме: уровень, ранг гильдии, характеристики и навыки."""

import datetime as dt
import math
import random

from . import theme as t
from .fonts import FontEmbedder
from .svg import PETAL_GRADIENT, document, esc, falling_petals, petal_css, truncate

CLASSES = {
    "Python": "Змеиный заклинатель",
    "JavaScript": "Иллюзионист JS",
    "TypeScript": "Рыцарь строгих типов",
    "Java": "Кофейный алхимик",
    "Kotlin": "Котлин-самурай",
    "C": "Повелитель памяти",
    "C++": "Некромант указателей",
    "C#": "Паладин .NET",
    "Go": "Ниндзя-суслик",
    "Rust": "Кузнец-краб",
    "Ruby": "Рубиновый маг",
    "PHP": "Старейшина слонов",
    "Swift": "Ласточка-разведчица",
    "Dart": "Метатель дротиков",
    "Lua": "Лунный маг",
    "Shell": "Шаман терминала",
    "PowerShell": "Шаман терминала",
    "HTML": "Архитектор разметки",
    "CSS": "Мастер стилей",
    "SCSS": "Мастер стилей",
    "Vue": "Призыватель компонентов",
    "Svelte": "Призыватель компонентов",
    "Jupyter Notebook": "Оракул данных",
    "R": "Оракул данных",
    "Haskell": "Монах лямбда-храма",
    "Elixir": "Алхимик эликсиров",
    "Assembly": "Древний рунописец",
    "GDScript": "Создатель миров",
}

# (условие, титул) — берётся первый подходящий.
TITLES = [
    (lambda s: s["streak_longest"] >= 100, "Бессмертный стрик"),
    (lambda s: s["contributions_year"] >= 2000, "Повелитель коммитов"),
    (lambda s: s["stars"] >= 100, "Звёздный странник"),
    (lambda s: s["streak_longest"] >= 30, "Неутомимый"),
    (lambda s: s["contributions_year"] >= 500, "Кодер-самурай"),
    (lambda s: s["followers"] >= 50, "Сэмпай гильдии"),
    (lambda s: s["prs_total"] >= 20, "Мастер пулл-реквестов"),
    (lambda s: s["public_repos"] >= 10, "Собиратель репозиториев"),
    (lambda s: s["contributions_year"] >= 100, "Подающий надежды"),
    (lambda s: True, "Новичок из стартовой деревни"),
]

RANKS = [(5, "F"), (10, "E"), (15, "D"), (22, "C"), (30, "B"), (40, "A"), (55, "S"), (75, "SS")]


def _fmt(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def compute(stats: dict, derived: dict, cfg: dict) -> dict:
    s = {**stats, **derived}
    xp = (s["contributions_year"] + s["stars"] * 10 + s["followers"] * 5
          + s["public_repos"] * 5 + s["prs_total"] * 3)
    level = 1 + int(math.sqrt(xp / 5))
    floor_xp, next_xp = 5 * (level - 1) ** 2, 5 * level ** 2
    rank = next((r for limit, r in RANKS if level < limit), "SSS")
    top_lang = s["languages"][0]["name"] if s["languages"] else None
    return {
        "xp": xp,
        "level": level,
        "xp_into": xp - floor_xp,
        "xp_span": next_xp - floor_xp,
        "rank": rank,
        "class": cfg.get("class") or CLASSES.get(top_lang, "Странствующий кодер"),
        "title": cfg.get("title") or next(title for cond, title in TITLES if cond(s)),
        "race": cfg.get("race", "Человек (?)"),
        "guild_year": s["created_at"][:4],
    }


def build(stats: dict, derived: dict, cfg: dict, fonts: FontEmbedder,
          exclude_languages: list[str] | None = None, now: dt.datetime | None = None) -> str:
    w, h = 900, 540
    rng = random.Random(5)
    now = now or dt.datetime.now(dt.timezone.utc)
    info = compute(stats, derived, cfg)

    langs = [lang for lang in stats["languages"] if lang["name"] not in (exclude_languages or [])]
    total_size = sum(lang["size"] for lang in langs) or 1
    langs = langs[:5]

    texts: list[str] = []  # всё, что попадёт на картинку, — для сабсета шрифта

    def text(x, y, value, size=13, weight=500, fill=t.TEXT, anchor="start", extra=""):
        value = str(value)
        texts.append(value)
        return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
                f'text-anchor="{anchor}" {extra}>{esc(value)}</text>')

    parts: list[str] = []

    # --- шапка окна ---
    parts.append(f'<rect x="34" y="37" width="10" height="10" fill="{t.CYAN}" transform="rotate(45 39 42)"/>')
    parts.append(text(54, 48, "STATUS", 15, 800, t.CYAN, extra='letter-spacing="5"'))
    parts.append(text(140, 48, "ステータス", 15, 700, t.PINK, extra='letter-spacing="2"'))
    parts.append(text(864, 47, f"Обновлено: {now:%d.%m.%Y · %H:%M} UTC", 12, 500, t.MUTED, "end"))
    parts.append('<rect x="36" y="64" width="828" height="1.5" fill="url(#hline)"/>')

    # --- левая колонка: персонаж ---
    parts.append(text(36, 110, truncate(stats["name"], 16), 30, 800, t.TEXT))
    texts.append(f"@{stats['login']} · Ранг гильдии {info['rank']}")
    parts.append(
        f'<text x="36" y="137" font-size="14" font-weight="500" fill="{t.MUTED}">'
        f'@{esc(stats["login"])} · Ранг гильдии '
        f'<tspan fill="{t.GOLD}" font-weight="800" font-size="16">{info["rank"]}</tspan></text>'
    )
    parts.append(f'<rect x="338" y="82" width="92" height="64" rx="14" fill="{t.PINK}" fill-opacity=".08" '
                 f'stroke="{t.PINK}" stroke-width="1.5" class="pulse"/>')
    parts.append(text(384, 103, "LV", 11, 800, t.CYAN, "middle", 'letter-spacing="3"'))
    parts.append(text(384, 136, info["level"], 30, 800, t.PINK, "middle"))

    rows = [
        ("Класс", info["class"]),
        ("Титул", f"«{info['title']}»"),
        ("Раса", info["race"]),
        ("Гильдия", f"GitHub · с {info['guild_year']} г."),
    ]
    for i, (label, value) in enumerate(rows):
        y = 180 + i * 26
        parts.append(text(36, y, label, 13, 500, t.MUTED))
        parts.append(text(118, y, truncate(value, 34), 14, 700 if i < 2 else 500, t.TEXT))

    bars = [
        ("EXP", "опыт до следующего уровня", info["xp_into"], info["xp_span"],
         f"{_fmt(info['xp_into'])} / {_fmt(info['xp_span'])}", "url(#gExp)", t.PINK),
        ("HP", "серия дней с коммитами", derived["streak_current"], max(derived["streak_longest"], 1),
         f"{derived['streak_current']} дн. · рекорд {derived['streak_longest']}", "url(#gHp)", t.PINK_DEEP),
        ("MP", "активных дней из 30", derived["active_days_30"], 30,
         f"{derived['active_days_30']} / 30", "url(#gMp)", t.CYAN),
    ]
    for i, (tag, desc, value, maximum, label, grad, color) in enumerate(bars):
        y = 302 + i * 50
        ratio = max(0.0, min(1.0, value / maximum)) if maximum else 0.0
        parts.append(text(36, y, tag, 12, 800, color, extra='letter-spacing="2"'))
        parts.append(text(36 + len(tag) * 9 + 10, y, desc, 12, 500, t.MUTED))
        parts.append(text(430, y, label, 12, 700, t.TEXT, "end"))
        parts.append(f'<rect x="36" y="{y + 9}" width="394" height="10" rx="5" fill="#ffffff" fill-opacity=".07"/>')
        if ratio > 0:
            parts.append(f'<rect class="grow" style="animation-delay:{0.2 + i * 0.25:.2f}s" x="36" y="{y + 9}" '
                         f'width="{max(394 * ratio, 6):.1f}" height="10" rx="5" fill="{grad}"/>')

    # --- правая колонка: характеристики ---
    parts.append(text(470, 100, "能力値 · Характеристики", 13, 700, t.CYAN, extra='letter-spacing="2"'))
    cells = [
        ("STR", "коммиты за год", stats["commits_year"]),
        ("INT", "пулл-реквесты", stats["prs_total"]),
        ("DEX", "issues", stats["issues_total"]),
        ("VIT", "макс. серия, дн.", derived["streak_longest"]),
        ("CHA", "подписчики", stats["followers"]),
        ("LUK", "звёзды", stats["stars"]),
    ]
    for i, (abbr, desc, value) in enumerate(cells):
        x, y = 470 + (i % 2) * 204, 114 + (i // 2) * 66
        parts.append(f'<rect x="{x}" y="{y}" width="190" height="56" rx="12" fill="{t.LAVENDER}" '
                     f'fill-opacity=".06" stroke="{t.LAVENDER}" stroke-opacity=".22"/>')
        parts.append(text(x + 14, y + 23, abbr, 12, 800, t.PINK, extra='letter-spacing="2"'))
        parts.append(text(x + 14, y + 42, desc, 11, 500, t.MUTED))
        parts.append(text(x + 176, y + 38, _fmt(value), 24, 800, t.TEXT, "end"))

    # --- навыки (языки) ---
    parts.append(text(470, 334, "スキル · Навыки", 13, 700, t.CYAN, extra='letter-spacing="2"'))
    if langs:
        top_share = langs[0]["size"] / total_size
        for i, lang in enumerate(langs):
            y = 358 + i * 22
            share = lang["size"] / total_size
            color = lang.get("color") or t.LAVENDER
            parts.append(f'<circle cx="476" cy="{y - 4}" r="5" fill="{color}"/>')
            parts.append(text(488, y, truncate(lang["name"], 15), 13, 500, t.TEXT))
            parts.append(f'<rect x="616" y="{y - 8}" width="196" height="6" rx="3" fill="#ffffff" fill-opacity=".07"/>')
            parts.append(f'<rect class="grow" style="animation-delay:{0.4 + i * 0.12:.2f}s" x="616" y="{y - 8}" '
                         f'width="{max(196 * share / top_share, 4):.1f}" height="6" rx="3" fill="{color}"/>')
            parts.append(text(864, y, f"{share * 100:.1f}%", 12, 500, t.MUTED, "end"))
    else:
        parts.append(text(470, 366, "Навыки ещё не раскрыты… (・_・;)", 14, 500, t.MUTED))

    # --- нижняя полоса: снаряжение и журнал ---
    parts.append('<rect x="36" y="466" width="828" height="1" fill="url(#hline)" opacity=".6"/>')
    parts.append(text(36, 490, "装備 · Снаряжение", 12, 700, t.CYAN, extra='letter-spacing="2"'))
    equipment = " · ".join(cfg.get("equipment", [])) or "Пока только палка и крышка от кастрюли"
    parts.append(text(36, 514, truncate(equipment, 82), 13, 500, t.TEXT))

    weekly = derived["weekly"] or [0]
    journal = f"Журнал приключений · {len(weekly)} нед." if derived["weekly"] else "Журнал приключений"
    parts.append(text(864, 490, journal, 12, 700, t.CYAN, "end", 'letter-spacing="1"'))
    peak = max(weekly) or 1
    bar_w, gap = 6, 2.2
    start_x = 864 - len(weekly) * (bar_w + gap) + gap
    for i, v in enumerate(weekly):
        bh = max(2.0, 24 * v / peak)
        parts.append(f'<rect class="growY" style="animation-delay:{0.5 + i * 0.03:.2f}s" '
                     f'x="{start_x + i * (bar_w + gap):.1f}" y="{522 - bh:.1f}" width="{bar_w}" '
                     f'height="{bh:.1f}" rx="2" fill="url(#gExp)" opacity="{0.45 + 0.55 * v / peak:.2f}"/>')

    defs = f"""
<clipPath id="panel"><rect x="8" y="8" width="884" height="524" rx="20"/></clipPath>
<linearGradient id="panelBg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#171038"/><stop offset="1" stop-color="#0d0a24"/></linearGradient>
<linearGradient id="border" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset=".5" stop-color="{t.LAVENDER}"/>
  <stop offset="1" stop-color="{t.CYAN}"/></linearGradient>
<linearGradient id="hline" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset=".6" stop-color="{t.LAVENDER}"/>
  <stop offset="1" stop-color="{t.CYAN}" stop-opacity="0"/></linearGradient>
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{t.CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{t.CYAN}" stop-opacity=".06"/>
  <stop offset="1" stop-color="{t.CYAN}" stop-opacity="0"/></linearGradient>
<linearGradient id="gExp" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset="1" stop-color="{t.LAVENDER}"/></linearGradient>
<linearGradient id="gHp" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PINK_DEEP}"/><stop offset="1" stop-color="{t.PINK_LIGHT}"/></linearGradient>
<linearGradient id="gMp" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PURPLE}"/><stop offset="1" stop-color="{t.CYAN}"/></linearGradient>
<filter id="glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="6"/></filter>
{PETAL_GRADIENT}
"""
    css = petal_css(h + 40, -120) + """
.grow { animation: grow 1.6s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: left center; }
@keyframes grow { from { transform: scaleX(0); } }
.growY { animation: growY 1.2s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: center bottom; }
@keyframes growY { from { transform: scaleY(0); } }
.scan { animation: scan 7s linear infinite; }
@keyframes scan { from { transform: translateY(-80px); } to { transform: translateY(560px); } }
.halo { animation: halo 4s ease-in-out infinite alternate; }
@keyframes halo { from { opacity: .25; } to { opacity: .6; } }
.pulse { animation: pulse 2.6s ease-in-out infinite alternate; }
@keyframes pulse { from { stroke-opacity: .4; } to { stroke-opacity: 1; } }
.blinkT { animation: blinkT 1.2s steps(2, start) infinite; }
@keyframes blinkT { to { visibility: hidden; } }
"""
    corner = 22
    corners = "".join(
        f'<path d="M{x},{y + dy * corner} V{y} H{x + dx * corner}" fill="none" stroke="{t.PINK}" '
        f'stroke-width="2.5" stroke-linecap="round"/>'
        for x, y, dx, dy in ((14, 14, 1, 1), (886, 14, -1, 1), (14, 526, 1, -1), (886, 526, -1, -1))
    )
    body = f"""
<rect class="halo" x="8" y="8" width="884" height="524" rx="20" fill="none" stroke="url(#border)"
      stroke-width="6" filter="url(#glow)"/>
<rect x="8" y="8" width="884" height="524" rx="20" fill="url(#panelBg)"/>
<g clip-path="url(#panel)">
  {falling_petals(rng, 8, w, h, 0.4, 0.7, 0.3)}
  <rect class="scan" x="8" y="0" width="884" height="80" fill="url(#scan)"/>
</g>
<rect x="8" y="8" width="884" height="524" rx="20" fill="none" stroke="url(#border)" stroke-width="1.5"/>
{corners}
{''.join(parts)}
<rect class="blinkT" x="232" y="35" width="7" height="15" rx="1.5" fill="{t.PINK}"/>
"""
    font_css = fonts.css("".join(texts) + "0123456789", (500, 700, 800))
    return document(w, h, f"Статус: {stats['name']} — Lv. {info['level']}", defs, css, body, font_css)
