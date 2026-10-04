#!/usr/bin/env python3
"""Пересобирает все анимешные карточки профиля в assets/generated/.

Запускается из GitHub Actions (см. .github/workflows/anime-profile.yml), но можно и локально:

    GITHUB_TOKEN=... python3 scripts/build.py
    python3 scripts/build.py --snapshot stats.json   # без обращения к GitHub API
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anime_profile import anime_list, github_stats, quote, scenery, status_window  # noqa: E402
from anime_profile.fonts import FontEmbedder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "generated"
README = ROOT / "README.md"


def write(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  ✿ {name} ({len(content.encode()) // 1024} KB)")


def replace_block(text: str, marker: str, content: str) -> str:
    pattern = re.compile(rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)", re.S)
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", text)


def add_snake_background(path: Path) -> None:
    """У змейки прозрачный фон — подкладываем ночную карточку, чтобы она смотрелась в любой теме GitHub."""
    if not path.exists():
        return
    svg = path.read_text(encoding="utf-8")
    if 'id="sakura-bg"' in svg:
        return
    m = re.search(r'viewBox="([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)"', svg)
    if not m:
        return
    x, y, w, h = (float(v) for v in m.groups())
    rect = (f'<rect id="sakura-bg" x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#120d2b"/>')
    svg = re.sub(r"(<svg\b[^>]*>)", lambda mm: mm.group(1) + rect, svg, count=1)
    path.write_text(svg, encoding="utf-8")
    print("  ✿ snake.svg — добавлен фон")


PLACEHOLDERS = {
    # файл: (ширина, высота, подпись) — рисуются, только если GitHub Actions ещё не создал настоящую картинку
    "stats.svg": (467, 195, "Статистика появится после первого запуска Actions"),
    "top-langs.svg": (300, 195, "Языки появятся после запуска Actions"),
    "snake.svg": (880, 192, "Змейка выползет после первого запуска Actions"),
    "3d-sakura.svg": (1280, 520, "3D-календарь появится после первого запуска Actions"),
}


def ensure_placeholders(fonts: FontEmbedder) -> None:
    for name, (w, h, label) in PLACEHOLDERS.items():
        if not (OUT / name).exists():
            write(name, scenery.build_placeholder(w, h, label, fonts))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", help="JSON со статистикой GitHub вместо запроса к API")
    parser.add_argument("--no-fonts", action="store_true", help="не встраивать шрифты (офлайн)")
    parser.add_argument("--no-anime", action="store_true", help="не ходить в AniList/Shikimori")
    args = parser.parse_args()

    cfg = json.loads((ROOT / "config" / "profile.json").read_text(encoding="utf-8"))
    quotes = json.loads((ROOT / "data" / "quotes.json").read_text(encoding="utf-8"))
    fonts = FontEmbedder(enabled=not args.no_fonts)
    login = cfg.get("github_username") or os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    ok = True

    print("🌸 Декорации")
    write("header.svg", scenery.build_header(cfg["header"], fonts))
    write("divider.svg", scenery.build_divider())
    write("footer.svg", scenery.build_footer(cfg["footer"], fonts))

    print("💬 Цитата дня")
    write("quote.svg", quote.build(quotes, fonts))

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
        write("status.svg", status_window.build(stats, derived, cfg.get("status_window", {}), fonts,
                                                cfg.get("exclude_languages", [])))
    except Exception as exc:
        ok = False
        print(f"  ✗ статистика не обновлена: {exc}", file=sys.stderr)

    print("📺 Сейчас смотрю")
    anime_cfg = cfg.get("anime_list", {})
    block = ("<!-- Впиши свой ник AniList или Shikimori в config/profile.json → anime_list, "
             "и здесь появится карточка «Сейчас смотрю» -->")
    if anime_cfg.get("username") and not args.no_anime:
        try:
            data = anime_list.fetch(anime_cfg)
            write("anime.svg", anime_list.build(data, anime_cfg["username"], fonts,
                                                anime_cfg.get("max_items", 5)))
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
    if block is not None and README.exists():
        README.write_text(replace_block(README.read_text(encoding="utf-8"), "ANIME-LIST", block),
                          encoding="utf-8")

    print("🧩 Заглушки и змейка")
    ensure_placeholders(fonts)
    add_snake_background(OUT / "snake.svg")
    print("готово ✨" if ok else "готово, но с ошибками (см. выше)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
