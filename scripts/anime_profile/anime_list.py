"""Карточка «Сейчас смотрю» по данным AniList или Shikimori (публичные API, токен не нужен)."""

import base64
import json
import sys
import urllib.parse
import urllib.request

from . import theme as t
from .fonts import FontEmbedder
from .svg import PETAL_GRADIENT, document, esc, flower, wrap

_UA = "anime-profile-readme (github profile generator)"

_ANILIST_QUERY = """
query ($name: String) {
  User(name: $name) {
    name
    siteUrl
    statistics { anime { count episodesWatched minutesWatched meanScore } }
  }
  MediaListCollection(userName: $name, type: ANIME, status: CURRENT, sort: UPDATED_TIME_DESC) {
    lists {
      entries {
        progress
        media {
          title { romaji english native }
          episodes
          nextAiringEpisode { episode }
          coverImage { large }
        }
      }
    }
  }
}
"""


def _http(url: str, data: bytes | None = None, headers: dict | None = None) -> tuple[bytes, str]:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": _UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")


def _anilist(username: str, title_lang: str) -> dict:
    body = json.dumps({"query": _ANILIST_QUERY, "variables": {"name": username}}).encode()
    raw, _ = _http("https://graphql.anilist.co", body,
                   {"Content-Type": "application/json", "Accept": "application/json"})
    data = json.loads(raw)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    user = data["data"]["User"]
    entries = [e for lst in data["data"]["MediaListCollection"]["lists"] for e in lst["entries"]]
    stats = user["statistics"]["anime"]
    items = []
    for e in entries:
        m = e["media"]
        titles = m["title"]
        title = titles.get(title_lang) or titles.get("english") or titles.get("romaji") or titles.get("native")
        aired = (m.get("nextAiringEpisode") or {}).get("episode")
        items.append({
            "title": title,
            "progress": e.get("progress") or 0,
            "total": m.get("episodes") or (aired - 1 if aired else None),
            "cover": m["coverImage"]["large"],
        })
    return {
        "service": "AniList",
        "url": user["siteUrl"],
        "items": items,
        "summary": (f"Всего аниме: {stats['count']} · эпизодов: {stats['episodesWatched']} · "
                    f"дней: {stats['minutesWatched'] / 1440:.1f} · ср. оценка: {stats['meanScore']:g}"),
    }


def _shikimori(username: str, domain: str) -> dict:
    domain = domain.rstrip("/")
    nick = urllib.parse.quote(username)
    raw, _ = _http(f"{domain}/api/users/{nick}/anime_rates?status=watching&limit=50")
    rates = sorted(json.loads(raw), key=lambda r: r.get("updated_at") or "", reverse=True)
    items = []
    for r in rates:
        a = r["anime"]
        total = a.get("episodes") or a.get("episodes_aired") or None
        image = (a.get("image") or {}).get("original") or ""
        items.append({
            "title": a.get("russian") or a.get("name"),
            "progress": r.get("episodes") or 0,
            "total": total,
            "cover": urllib.parse.urljoin(domain + "/", image) if image else "",
        })
    return {
        "service": "Shikimori",
        "url": f"{domain}/{nick}",
        "items": items,
        "summary": f"Смотрю сейчас: {len(items)} тайтл(ов)",
    }


def fetch(cfg: dict) -> dict | None:
    service = (cfg.get("service") or "anilist").lower()
    username = (cfg.get("username") or "").strip()
    if not username:
        return None
    if service == "shikimori":
        return _shikimori(username, cfg.get("shikimori_domain") or "https://shikimori.one")
    return _anilist(username, cfg.get("title_language") or "english")


def _data_uri(url: str) -> str | None:
    if not url:
        return None
    try:
        raw, ctype = _http(url)
    except Exception as exc:
        print(f"[anime] обложка не скачалась: {url}: {exc}", file=sys.stderr)
        return None
    mime = ctype.split(";")[0].strip() or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def build(data: dict, username: str, fonts: FontEmbedder, max_items: int = 5,
          embed_covers: bool = True) -> str:
    w = 900
    items = data["items"][:max_items]
    header = "視聴中 · Сейчас смотрю"
    service = f"{data['service']} · {username}"
    texts = [header, service, data["summary"], "эп. 0123456789/?…"]

    parts = [
        f'<rect x="34" y="37" width="10" height="10" fill="{t.CYAN}" transform="rotate(45 39 42)"/>',
        f'<text x="54" y="48" font-size="15" font-weight="800" fill="{t.PINK}" letter-spacing="2">{esc(header)}</text>',
        f'<text x="864" y="48" font-size="12" font-weight="700" fill="{t.CYAN}" text-anchor="end">{esc(service)}</text>',
        f'<text x="54" y="74" font-size="13" font-weight="500" fill="{t.MUTED}">{esc(data["summary"])}</text>',
        '<rect x="36" y="88" width="828" height="1.5" fill="url(#hline)"/>',
    ]
    clips = []

    if not items:
        h = 180
        msg = "Сейчас ничего не смотрю… выбираю следующий тайтл (´・ω・`)"
        texts.append(msg)
        parts.append(f'<text x="450" y="136" font-size="16" font-weight="500" fill="{t.TEXT}" '
                     f'text-anchor="middle">{esc(msg)}</text>')
    else:
        h = 400
        col_w, gap = 164, 10
        x0 = (w - (len(items) * col_w + (len(items) - 1) * gap)) / 2
        for i, item in enumerate(items):
            cx = x0 + i * (col_w + gap) + col_w / 2
            ix, iy, iw, ih = cx - 64, 106, 128, 180
            clips.append(f'<clipPath id="c{i}"><rect x="{ix:.1f}" y="{iy}" width="{iw}" height="{ih}" rx="12"/></clipPath>')
            uri = _data_uri(item["cover"]) if embed_covers else None
            parts.append(f'<g class="rise" style="animation-delay:{i * 0.12:.2f}s">')
            if uri:
                parts.append(f'<image href="{uri}" x="{ix:.1f}" y="{iy}" width="{iw}" height="{ih}" '
                             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#c{i})"/>')
            else:
                parts.append(f'<rect x="{ix:.1f}" y="{iy}" width="{iw}" height="{ih}" rx="12" fill="url(#ph)"/>')
                parts.append(flower(cx, iy + ih / 2, 1.6))
            parts.append(f'<rect x="{ix:.1f}" y="{iy}" width="{iw}" height="{ih}" rx="12" fill="none" '
                         f'stroke="url(#border)" stroke-width="1.5"/>')
            title_lines = wrap(item["title"] or "???", 19, 2)
            texts.extend(title_lines)
            for j, line in enumerate(title_lines):
                parts.append(f'<text x="{cx:.1f}" y="{iy + ih + 24 + j * 18}" font-size="13" font-weight="700" '
                             f'fill="{t.TEXT}" text-anchor="middle">{esc(line)}</text>')
            total = item["total"]
            ratio = min(1.0, item["progress"] / total) if total else 0.0
            by = iy + ih + 66
            parts.append(f'<rect x="{ix:.1f}" y="{by}" width="{iw}" height="6" rx="3" fill="#ffffff" fill-opacity=".08"/>')
            if ratio > 0:
                parts.append(f'<rect class="grow" x="{ix:.1f}" y="{by}" width="{max(iw * ratio, 4):.1f}" height="6" '
                             f'rx="3" fill="url(#gBar)"/>')
            label = f"эп. {item['progress']} / {total or '?'}"
            parts.append(f'<text x="{cx:.1f}" y="{by + 24}" font-size="12" font-weight="500" fill="{t.MUTED}" '
                         f'text-anchor="middle">{esc(label)}</text>')
            parts.append("</g>")

    defs = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#1a1140"/><stop offset="1" stop-color="#0d0a24"/></linearGradient>
<linearGradient id="border" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset="1" stop-color="{t.LAVENDER}"/></linearGradient>
<linearGradient id="hline" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset=".6" stop-color="{t.LAVENDER}"/>
  <stop offset="1" stop-color="{t.CYAN}" stop-opacity="0"/></linearGradient>
<linearGradient id="gBar" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t.PINK}"/><stop offset="1" stop-color="{t.CYAN}"/></linearGradient>
<linearGradient id="ph" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#3b1a5c"/><stop offset="1" stop-color="#1d1145"/></linearGradient>
{PETAL_GRADIENT}
{''.join(clips)}
"""
    css = """
.rise { animation: rise 1.2s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
.grow { animation: grow 1.6s cubic-bezier(.2,.8,.2,1) .4s both; transform-box: fill-box; transform-origin: left center; }
@keyframes grow { from { transform: scaleX(0); } }
"""
    body = (f'<rect x="8" y="8" width="{w - 16}" height="{h - 16}" rx="20" fill="url(#bg)" '
            f'stroke="url(#border)" stroke-width="1.5"/>\n' + "\n".join(parts))
    font_css = fonts.css("".join(texts), (500, 700, 800))
    return document(w, h, f"Сейчас смотрю ({data['service']})", defs, css, body, font_css)
