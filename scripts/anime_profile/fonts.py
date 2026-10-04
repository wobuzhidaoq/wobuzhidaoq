"""Встраивание шрифта в SVG.

SVG, вставленный в README через <img>, не может грузить внешние ресурсы,
поэтому берём у Google Fonts крошечный сабсет шрифта ровно под символы,
которые есть на картинке, и кладём его внутрь SVG в base64.
Если сеть недоступна — молча откатываемся на системные шрифты.
"""

import base64
import re
import sys
import urllib.parse
import urllib.request

from .theme import FONT_FAMILY

_CSS_URL = "https://fonts.googleapis.com/css2?family={family}:wght@{weights}&text={text}"
_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


class FontEmbedder:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._cache: dict[tuple, str] = {}

    def css(self, text: str, weights: tuple[int, ...]) -> str:
        """Возвращает блок @font-face с встроенным сабсетом (или пустую строку)."""
        if not self.enabled:
            return ""
        chars = "".join(sorted({c for c in text if not c.isspace()}))
        key = (chars, weights)
        if key in self._cache:
            return self._cache[key]
        try:
            url = _CSS_URL.format(
                family=urllib.parse.quote_plus(FONT_FAMILY),
                weights=";".join(str(w) for w in sorted(weights)),
                text=urllib.parse.quote(chars, safe=""),
            )
            css = _get(url).decode("utf-8")

            def inline(match: re.Match) -> str:
                font_url = match.group(1)
                data = base64.b64encode(_get(font_url)).decode("ascii")
                mime = "font/woff2" if "woff2" in match.group(2) else "font/ttf"
                return f"url(data:{mime};base64,{data}) format('{match.group(2)}')"

            css = re.sub(r"url\((https://[^)]+)\)\s*format\('([^']+)'\)", inline, css)
            css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
            css = re.sub(r"\s+", " ", css).strip()
        except Exception as exc:  # сеть/Google Fonts недоступны — не страшно
            print(f"[fonts] не удалось встроить шрифт: {exc}", file=sys.stderr)
            css = ""
        self._cache[key] = css
        return css
