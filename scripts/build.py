#!/usr/bin/env python3
"""Пересобирает все карточки профиля в assets/generated/ и блоки виджетов в README.md.

Стиль выбирается в config/profile.json → "style" ("sakura-day" или "manga").
Запускается из GitHub Actions (см. .github/workflows/anime-profile.yml), но можно и локально:

    GITHUB_TOKEN=... python3 scripts/build.py
    python3 scripts/build.py --snapshot stats.json   # без обращения к GitHub API
"""

import argparse
import datetime as dt
import hashlib
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

def write(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  ✿ {name} ({len(content.encode()) // 1024} KB)")


def replace_block(text: str, marker: str, content: str) -> str:
    pattern = re.compile(rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)", re.S)
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", text)


def bust_cache(readme: str) -> str:
    """Добавляет к ссылкам на картинки ?v=<отпечаток файла>: изменилась картинка — изменилась ссылка,
    и браузер/GitHub сразу показывают свежую версию, а не старую из кэша."""
    def version(m: re.Match) -> str:
        path = ROOT / m.group(1)
        if not path.is_file():
            return m.group(1)
        return f"{m.group(1)}?v={hashlib.sha1(path.read_bytes()).hexdigest()[:10]}"
    return re.sub(r"(\./assets/generated/[\w.-]+\.svg)(\?v=[0-9a-f]+)?", version, readme)


def load_config() -> tuple[dict, str, dict]:
    cfg = json.loads((ROOT / "config" / "profile.json").read_text(encoding="utf-8"))
    cfg["github_username"] = cfg.get("github_username") or os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    name = cfg.get("style", "sakura-day")
    style_cfg = json.loads((ROOT / "config" / "styles" / f"{name}.json").read_text(encoding="utf-8"))
    return cfg, name, style_cfg


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", help="JSON со статистикой GitHub вместо запроса к API")
    parser.add_argument("--no-fonts", action="store_true", help="не встраивать шрифты (офлайн)")
    parser.add_argument("--no-anime", action="store_true", help="не ходить в AniList/Shikimori")
    args = parser.parse_args()

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

    pinned = (cfg.get("quote") or {}).get("text")
    write("views.svg", style.views_caption(cfg.get("views", {}), ctx))

    print("💬 Цитата" + (" (закреплённая)" if pinned else " дня"))
    write("quote.svg", style.quote([cfg["quote"]] if pinned else quotes, ctx, pinned=bool(pinned)))

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
        status_cfg = {**cfg.get("status_window", {}), "skills": widgets.skill_rows(cfg)}
        write("status.svg", style.status(stats, derived, status_cfg, ctx, cfg.get("exclude_languages", [])))
    except Exception as exc:
        ok = False
        print(f"  ✗ статистика не обновлена: {exc}", file=sys.stderr)

    readme = README.read_text(encoding="utf-8") if README.exists() else None

    print("📺 Сейчас смотрю")
    anime_cfg = cfg.get("anime_list", {})
    block = ("<!-- Put your AniList or Shikimori username into config/profile.json → anime_list "
             "to show a 'Now watching' card here -->")
    if anime_cfg.get("username") and not args.no_anime:
        try:
            data = anime_list.fetch(anime_cfg)
            write("anime.svg", style.anime(data, anime_cfg["username"], ctx, anime_cfg.get("max_items", 5)))
            block = (
                '<p align="center"><img src="./assets/generated/divider.svg" width="100%" alt=""/></p>\n\n'
                '<h2 align="center">📺 Now watching · 視聴中</h2>\n\n'
                f'<p align="center"><a href="{data["url"]}">'
                '<img src="./assets/generated/anime.svg" width="100%" alt="What I’m watching now"/></a></p>'
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

    if readme is not None:
        README.write_text(bust_cache(readme), encoding="utf-8")
    print("готово ✨" if ok else "готово, но с ошибками (см. выше)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
