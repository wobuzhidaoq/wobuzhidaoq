"""Блоки README с внешними виджетами (печатающийся текст, бейджи, навыки, счётчик).

Цвета берутся из config/styles/<стиль>.json, тексты и списки — из config/profile.json,
поэтому при смене стиля README перекрашивается сам, а твои тексты остаются.
"""

from urllib.parse import quote, quote_plus, urlencode

# id из skillicons.dev → (подпись, иконка из simpleicons.org, цвет языка)
SKILLS = {
    "ts": ("TypeScript", "typescript", "#3178c6"), "js": ("JavaScript", "javascript", "#f1e05a"),
    "react": ("React", "react", "#61dafb"), "tailwind": ("Tailwind CSS", "tailwindcss", "#38bdf8"),
    "shadcn": ("shadcn/ui", "shadcnui", "#111111"), "nextjs": ("Next.js", "nextdotjs", "#111111"),
    "vue": ("Vue", "vuedotjs", "#41b883"), "svelte": ("Svelte", "svelte", "#ff3e00"),
    "html": ("HTML", "html5", "#e34c26"), "css": ("CSS", "css", "#663399"), "sass": ("Sass", "sass", "#cc6699"),
    "nodejs": ("Node.js", "nodedotjs", "#5fa04e"), "deno": ("Deno", "deno", "#111111"),
    "vite": ("Vite", "vite", "#646cff"), "redux": ("Redux", "redux", "#764abc"),
    "rust": ("Rust", "rust", "#dea584"), "cpp": ("C++", "cplusplus", "#f34b7d"), "c": ("C", "c", "#555555"),
    "cs": ("C#", "", "#178600"), "go": ("Go", "go", "#00add8"), "java": ("Java", "openjdk", "#b07219"),
    "kotlin": ("Kotlin", "kotlin", "#a97bff"), "swift": ("Swift", "swift", "#f05138"),
    "dart": ("Dart", "dart", "#00b4ab"), "flutter": ("Flutter", "flutter", "#02569b"),
    "python": ("Python", "python", "#3572a5"), "php": ("PHP", "php", "#4f5d95"), "ruby": ("Ruby", "ruby", "#701516"),
    "lua": ("Lua", "lua", "#000080"), "zig": ("Zig", "zig", "#ec915c"), "wasm": ("WebAssembly", "webassembly", "#654ff0"),
    "git": ("Git", "git", "#f05032"), "github": ("GitHub", "github", "#111111"),
    "vscode": ("VS Code", "", "#007acc"), "neovim": ("Neovim", "neovim", "#57a143"),
    "linux": ("Linux", "linux", "#111111"), "docker": ("Docker", "docker", "#2496ed"),
    "postgres": ("PostgreSQL", "postgresql", "#4169e1"), "figma": ("Figma", "figma", "#f24e1e"),
}
# Этих иконок нет на skillicons.dev — для них рисуем бейдж
NOT_IN_SKILLICONS = {"shadcn", "wasm"}


def skill_groups(cfg: dict) -> list[dict]:
    """Навыки из config/profile.json → skills: либо простой список, либо группы с уровнем."""
    raw = cfg.get("skills", [])
    if raw and isinstance(raw[0], str):
        raw = [{"group": "", "items": raw}]
    groups = []
    for i, g in enumerate(raw):
        items = [{"id": sid, "name": SKILLS.get(sid, (sid.capitalize(), "", ""))[0],
                  "logo": SKILLS.get(sid, ("", sid, ""))[1], "color": SKILLS.get(sid, ("", "", ""))[2] or "#b18cff"}
                 for sid in g.get("items", [])]
        groups.append({"title": g.get("group", ""), "level": g.get("level", ""),
                       "power": g.get("power", 80 if i == 0 else 35), "items": items})
    return groups


def skill_rows(cfg: dict) -> list[dict]:
    """Плоский список навыков для окна статуса: имя, цвет, уровень, «сила» 0..1."""
    return [{"name": it["name"], "color": it["color"], "level": g["level"], "power": g["power"] / 100, "group": gi}
            for gi, g in enumerate(skill_groups(cfg)) for it in g["items"]]


def _shield(label: str, message: str, color: str, label_color: str, logo: str = "", alt: str = "") -> str:
    def part(text: str) -> str:
        # «/» в адресе бейджа ломает путь — заменяем на похожий символ деления «∕»
        return quote(text.replace("-", "--").replace("_", "__").replace("/", "∕"), safe="")
    path = f"{part(label)}-{part(message)}-{color}" if message else f"{part(label)}-{color}"
    params = {"style": "for-the-badge", "labelColor": label_color}
    if logo:
        params.update(logo=logo, logoColor="white")
    return f'<img src="https://img.shields.io/badge/{path}?{urlencode(params)}" alt="{alt or label}"/>'


def typing(cfg: dict, style: dict) -> str:
    t = style["typing"]
    params = (f"font={quote_plus(t['font'])}&weight={t['weight']}&size=22&duration=3000&pause=1000"
              f"&color={t['color']}&center=true&vCenter=true&width=720&height=46")
    lines = ";".join(quote_plus(line) for line in cfg.get("typing_lines", []))
    login = cfg.get("github_username", "")
    return (f'<p align="center">\n  <a href="https://github.com/{login}">\n'
            f'    <img src="https://readme-typing-svg.demolab.com?{params}&lines={lines}" '
            f'alt="Печатающийся текст с приветствием"/>\n  </a>\n</p>')


def badges(cfg: dict, style: dict) -> str:
    b = style["badges"]
    login = cfg.get("github_username", "")
    followers = (f'<a href="https://github.com/{login}?tab=followers"><img src="https://img.shields.io/github/'
                 f'followers/{login}?{urlencode({"label": "Подписчики", "style": "for-the-badge", "logo": "github", "logoColor": "white", "color": b["followers"]["color"], "labelColor": b["followers"]["labelColor"]})}" '
                 f'alt="Подписчики"/></a>')
    items = [
        followers,
        _shield("Уровень силы", "больше 9000!", b["power"]["color"], b["power"]["labelColor"]),
        _shield("Аниме-статус", "смотрю ещё одну серию", b["anime"]["color"], b["anime"]["labelColor"],
                "crunchyroll"),
    ]
    colors = b["social"]
    for i, social in enumerate(s for s in cfg.get("socials", []) if s.get("url")):
        color = colors[i % len(colors)]
        items.append(f'<a href="{social["url"]}">'
                     f'{_shield(social["name"], "", color, color, social.get("logo", ""))}</a>')
    return '<p align="center">\n  ' + "\n  ".join(items) + "\n</p>"


def skills(cfg: dict, style: dict) -> str:
    s = style["skills"]
    blocks = []
    for gi, group in enumerate(skill_groups(cfg)):
        if not group["items"]:
            continue
        if s["type"] == "skillicons":
            ids = [it["id"] for it in group["items"] if it["id"] not in NOT_IN_SKILLICONS]
            extra = [it for it in group["items"] if it["id"] in NOT_IN_SKILLICONS]
            row = []
            if ids:
                row.append(f'<img src="https://skillicons.dev/icons?i={",".join(ids)}'
                           f'&perline=12&theme={s.get("theme", "light")}" alt="{", ".join(i["name"] for i in group["items"] if i["id"] in ids)}"/>')
            row += [_shield(it["name"], "", it["color"].lstrip("#"), it["color"].lstrip("#"), it["logo"]) for it in extra]
        else:
            colors = s.get("colors", [s.get("color", "111111")])
            color = colors[min(gi, len(colors) - 1)]
            row = [_shield(it["name"], "", color, color, it["logo"]) for it in group["items"]]
        title = f'<p align="center"><b>{group["title"]}</b></p>\n' if group["title"] else ""
        blocks.append(title + '<p align="center">\n  ' + "\n  ".join(row) + "\n</p>")
    return "\n\n".join(blocks)


def views(cfg: dict, style: dict) -> str:
    login = cfg.get("github_username", "")
    params = urlencode({"name": login, "theme": style["views_theme"], "padding": 7, "offset": 0, "align": "top",
                        "scale": 1, "pixelated": 1, "darkmode": "auto"})
    credits = "".join(f"\n  <br/><sub>🎨 {c}</sub>" for c in cfg.get("credits", []))
    return (f'<p align="center">\n  <img src="https://count.getloli.com/@{login}?{params}" '
            f'alt="Счётчик просмотров профиля"/>{credits}\n</p>')


BLOCKS = {"TYPING": typing, "BADGES": badges, "SKILLS": skills, "VIEWS": views}
