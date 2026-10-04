#!/usr/bin/env python3
"""Пересобирает все карточки профиля в assets/generated/ и блоки виджетов в README.md.

Стиль выбирается в config/profile.json → "style" ("sakura-day" или "manga").
Запускается из GitHub Actions (см. .github/workflows/anime-profile.yml), но можно и локально:

    GITHUB_TOKEN=... python3 scripts/build.py
    python3 scripts/build.py --snapshot stats.json   # без обращения к GitHub API
    python3 scripts/build.py --actions-env           # настройки стиля для шагов workflow
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anime_profile import anime_list, github_stats, styles, widgets  # noqa: E402
from anime_profile.fonts import FontEmbedder  # noqa: E402
from anime_profile.images import ImageLoader  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "generated"
README = ROOT / "README.md"

PLACEHOLDERS = {
    # файл: (ширина, высота, подпись) — рисуются, только если GitHub Actions ещё не создал настоящую картинку
    "stats.svg": (467, 195, "Статистика появится после первого запуска Actions"),
    "top-langs.svg": (300, 195, "Языки появятся после запуска Actions"),
    "snake.svg": (880, 192, "Змейка выползет после первого запуска Actions"),
    "3d-sakura.svg": (1280, 520, "3D-календарь появится после первого запуска Actions"),
}


def write(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  ✿ {name} ({len(content.encode()) // 1024} KB)")


def replace_block(text: str, marker: str, content: str) -> str:
    pattern = re.compile(rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)", re.S)
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", text)


def load_config() -> tuple[dict, str, dict]:
    cfg = json.loads((ROOT / "config" / "profile.json").read_text(encoding="utf-8"))
    cfg["github_username"] = cfg.get("github_username") or os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    name = cfg.get("style", "sakura-day")
    style_cfg = json.loads((ROOT / "config" / "styles" / f"{name}.json").read_text(encoding="utf-8"))
    return cfg, name, style_cfg


def add_snake_background(path: Path, bg: dict) -> None:
    """У змейки прозрачный фон — подкладываем карточку в цветах стиля."""
    if not path.exists():
        return
    svg = re.sub(r'<rect id="sakura-bg"[^>]*/>', "", path.read_text(encoding="utf-8"))
    m = re.search(r'viewBox="([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)"', svg)
    if not m:
        return
    x, y, w, h = (float(v) for v in m.groups())
    rect = (f'<rect id="sakura-bg" x="{x + 1}" y="{y + 1}" width="{w - 2}" height="{h - 2}" rx="{bg["rx"]}" '
            f'fill="{bg["fill"]}" stroke="{bg["stroke"]}" stroke-width="2"/>')
    svg = re.sub(r"(<svg\b[^>]*>)", lambda mm: mm.group(1) + rect, svg, count=1)
    path.write_text(svg, encoding="utf-8")
    print("  ✿ snake.svg — фон в цветах стиля")


def make_grayscale(path: Path) -> None:
    """Обесцвечивает чужую картинку (например, 3D-календарь), если стиль чёрно-белый."""
    if not path.exists():
        return
    svg = path.read_text(encoding="utf-8")
    if 'id="bw-wrap"' in svg:
        return
    opening = re.search(r"<svg\b[^>]*>", svg)
    end = svg.rfind("</svg>")
    if not opening or end < 0:
        return
    head = ('<defs><filter id="bw-gray"><feColorMatrix type="saturate" values="0"/></filter></defs>'
            '<g id="bw-wrap" filter="url(#bw-gray)">')
    svg = svg[:opening.end()] + head + svg[opening.end():end] + "</g>" + svg[end:]
    path.write_text(svg, encoding="utf-8")
    print(f"  ✿ {path.name} — обесцвечено")


def actions_env() -> int:
    """Печатает настройки стиля в формате $GITHUB_OUTPUT для шагов workflow."""
    _, name, style_cfg = load_config()
    contrib = {**style_cfg["contrib3d"], "fileName": "profile-sakura.svg"}
    contrib_path = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "3d-style.json"
    contrib_path.write_text(json.dumps(contrib), encoding="utf-8")
    langs = style_cfg.get("langs_options")
    print(f"style={name}")
    print(f"stats_options={json.dumps(style_cfg['stats_options'], ensure_ascii=False)}")
    print(f"langs_options={json.dumps(langs, ensure_ascii=False) if langs else ''}")
    print(f"snake={style_cfg['snake']}")
    print(f"contrib3d={contrib_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", help="JSON со статистикой GitHub вместо запроса к API")
    parser.add_argument("--no-fonts", action="store_true", help="не встраивать шрифты (офлайн)")
    parser.add_argument("--no-anime", action="store_true", help="не ходить в AniList/Shikimori")
    parser.add_argument("--actions-env", action="store_true", help="вывести настройки стиля для workflow")
    args = parser.parse_args()
    if args.actions_env:
        return actions_env()

    cfg, style_name, style_cfg = load_config()
    style = styles.load(style_name)
    ctx = styles.Ctx(FontEmbedder(enabled=not args.no_fonts), ImageLoader(ROOT, cfg.get("images", {})))
    quotes = json.loads((ROOT / "data" / "quotes.json").read_text(encoding="utf-8"))
    login = cfg["github_username"]
    ok = True
    print(f"🎨 Стиль: {style_cfg.get('title', style_name)}")

    print("🌸 Декорации")
    write("header.svg", style.header(cfg["header"], ctx))
    write("divider.svg", style.divider(ctx))
    write("footer.svg", style.footer(cfg["footer"], ctx))

    print("💬 Цитата дня")
    write("quote.svg", style.quote(quotes, ctx))

    print("⚔️  Окно статуса")
    try:
        if args.snapshot:
            stats = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        else:
            token = os.environ.get("GITHUB_TOKEN")
            if not token or not login:
                raise RuntimeError("нужны GITHUB_TOKEN и github_username (или GITHUB_REPOSITORY_OWNER)")
            stats = github_stats.fetch(login, token)
        derived = github_stats.derive(stats, dt.datetime.now(dt.timezone.utc).date())
        write("status.svg", style.status(stats, derived, cfg.get("status_window", {}), ctx,
                                         cfg.get("exclude_languages", [])))
    except Exception as exc:
        ok = False
        print(f"  ✗ статистика не обновлена: {exc}", file=sys.stderr)

    readme = README.read_text(encoding="utf-8") if README.exists() else None

    print("📺 Сейчас смотрю")
    anime_cfg = cfg.get("anime_list", {})
    block = ("<!-- Впиши свой ник AniList или Shikimori в config/profile.json → anime_list, "
             "и здесь появится карточка «Сейчас смотрю» -->")
    if anime_cfg.get("username") and not args.no_anime:
        try:
            data = anime_list.fetch(anime_cfg)
            write("anime.svg", style.anime(data, anime_cfg["username"], ctx, anime_cfg.get("max_items", 5)))
            block = (
                '<p align="center"><img src="./assets/generated/divider.svg" width="100%" alt=""/></p>\n\n'
                '<h2 align="center">📺 Сейчас смотрю · 視聴中</h2>\n\n'
                f'<p align="center"><a href="{data["url"]}">'
                '<img src="./assets/generated/anime.svg" width="100%" alt="Что я сейчас смотрю"/></a></p>'
            )
        except Exception as exc:
            ok = False
            print(f"  ✗ список аниме не обновлён: {exc}", file=sys.stderr)
            block = None  # оставляем в README то, что было
    if readme is not None:
        if block is not None:
            readme = replace_block(readme, "ANIME-LIST", block)
        print("🧷 Виджеты в README")
        for marker, render in widgets.BLOCKS.items():
            readme = replace_block(readme, marker, render(cfg, style_cfg))
        README.write_text(readme, encoding="utf-8")

    print("🧩 Заглушки и змейка")
    for name, (w, h, label) in PLACEHOLDERS.items():
        if not (OUT / name).exists():
            write(name, style.placeholder(w, h, label, ctx))
    add_snake_background(OUT / "snake.svg", style_cfg["snake_background"])
    for name in style_cfg.get("grayscale", []):
        make_grayscale(OUT / name)
    print("готово ✨" if ok else "готово, но с ошибками (см. выше)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
