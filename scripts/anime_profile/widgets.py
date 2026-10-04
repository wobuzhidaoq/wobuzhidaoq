"""Блоки README с внешними виджетами (печатающийся текст, бейджи, навыки, статистика, счётчик).

Цвета берутся из config/styles/<стиль>.json, тексты и списки — из config/profile.json,
поэтому при смене стиля README перекрашивается сам, а твои тексты остаются.
"""

from urllib.parse import quote, quote_plus, urlencode

# id из skillicons.dev → (подпись, иконка из simpleicons.org) для чёрно-белых бейджей
SKILLS = {
    "python": ("Python", "python"), "js": ("JavaScript", "javascript"), "ts": ("TypeScript", "typescript"),
    "html": ("HTML", "html5"), "css": ("CSS", "css"), "react": ("React", "react"), "vue": ("Vue", "vuedotjs"),
    "svelte": ("Svelte", "svelte"), "nodejs": ("Node.js", "nodedotjs"), "deno": ("Deno", "deno"),
    "nextjs": ("Next.js", "nextdotjs"), "tailwind": ("Tailwind", "tailwindcss"), "sass": ("Sass", "sass"),
    "git": ("Git", "git"), "github": ("GitHub", "github"), "gitlab": ("GitLab", "gitlab"),
    "vscode": ("VS Code", ""), "vim": ("Vim", "vim"), "neovim": ("Neovim", "neovim"),
    "idea": ("IntelliJ", "intellijidea"), "pycharm": ("PyCharm", "pycharm"),
    "linux": ("Linux", "linux"), "ubuntu": ("Ubuntu", "ubuntu"), "arch": ("Arch", "archlinux"),
    "windows": ("Windows", ""), "apple": ("macOS", "apple"), "bash": ("Bash", "gnubash"),
    "docker": ("Docker", "docker"), "kubernetes": ("Kubernetes", "kubernetes"), "nginx": ("Nginx", "nginx"),
    "java": ("Java", "openjdk"), "kotlin": ("Kotlin", "kotlin"), "cpp": ("C++", "cplusplus"), "c": ("C", "c"),
    "cs": ("C#", ""), "go": ("Go", "go"), "rust": ("Rust", "rust"), "php": ("PHP", "php"),
    "ruby": ("Ruby", "ruby"), "swift": ("Swift", "swift"), "dart": ("Dart", "dart"),
    "flutter": ("Flutter", "flutter"), "lua": ("Lua", "lua"), "r": ("R", "r"),
    "postgres": ("PostgreSQL", "postgresql"), "mysql": ("MySQL", "mysql"), "mongodb": ("MongoDB", "mongodb"),
    "redis": ("Redis", "redis"), "sqlite": ("SQLite", "sqlite"), "django": ("Django", "django"),
    "flask": ("Flask", "flask"), "fastapi": ("FastAPI", "fastapi"), "unity": ("Unity", "unity"),
    "godot": ("Godot", "godotengine"), "blender": ("Blender", "blender"), "figma": ("Figma", "figma"),
    "discord": ("Discord", "discord"), "telegram": ("Telegram", "telegram"),
}


def _shield(label: str, message: str, color: str, label_color: str, logo: str = "", alt: str = "") -> str:
    def part(text: str) -> str:
        return quote(text.replace("-", "--").replace("_", "__"), safe="")
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
    ids = cfg.get("skills", [])
    if not ids:
        return ""
    s = style["skills"]
    if s["type"] == "skillicons":
        return (f'<p align="center">\n  <img src="https://skillicons.dev/icons?i={",".join(ids)}'
                f'&perline=12&theme={s.get("theme", "light")}" alt="Технологии"/>\n</p>')
    chips = []
    for skill in ids:
        label, logo = SKILLS.get(skill, (skill.capitalize(), skill))
        chips.append(_shield(label, "", s["color"], s["color"], logo))
    return '<p align="center">\n  ' + "\n  ".join(chips) + "\n</p>"


def stats(cfg: dict, style: dict) -> str:
    login = cfg.get("github_username", "")
    cards = ['  <img src="./assets/generated/stats.svg" height="180" alt="Статистика GitHub"/>']
    if style.get("langs_options"):
        cards.append('  <img src="./assets/generated/top-langs.svg" height="180" alt="Самые используемые языки"/>')
    streak = urlencode({"user": login, "locale": "ru", **style["streak"]})
    activity = urlencode({"username": login, **style["activity"], "custom_title": "Статистика активности · 活動"})
    return "\n\n".join([
        '<p align="center">\n' + "\n".join(cards) + "\n</p>",
        f'<p align="center">\n  <img src="https://streak-stats.demolab.com?{streak}" alt="Серия дней с коммитами"/>\n</p>',
        f'<p align="center">\n  <img src="https://github-readme-activity-graph.vercel.app/graph?{activity}" '
        f'width="100%" alt="График активности"/>\n</p>',
        '<p align="center">\n  <img src="./assets/generated/3d-sakura.svg" width="100%" '
        'alt="3D-календарь вкладов"/>\n</p>',
    ])


def views(cfg: dict, style: dict) -> str:
    login = cfg.get("github_username", "")
    params = urlencode({"name": login, "theme": style["views_theme"], "padding": 7, "offset": 0, "align": "top",
                        "scale": 1, "pixelated": 1, "darkmode": "auto"})
    credits = "".join(f"\n  <br/><sub>🎨 {c}</sub>" for c in cfg.get("credits", []))
    return (f'<p align="center">\n  <img src="https://count.getloli.com/@{login}?{params}" '
            f'alt="Счётчик просмотров профиля"/>\n  <br/>\n  <sub>☝️ столько путников уже заглянуло в профиль</sub>'
            f"{credits}\n</p>")


BLOCKS = {"TYPING": typing, "BADGES": badges, "SKILLS": skills, "STATS": stats, "VIEWS": views}
