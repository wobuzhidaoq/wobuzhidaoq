"""Картинки пользователя (assets/images/…) → data URI для вклейки внутрь SVG.

SVG, показанный через <img>, не может грузить внешние файлы, поэтому картинка
кладётся внутрь в base64. Если установлен Pillow — картинка уменьшается,
переводится в ч/б (по желанию) и пережимается, чтобы профиль грузился быстро.
"""

import base64
import io
import mimetypes
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # без Pillow просто вклеиваем файл как есть
    Image = None


class ImageLoader:
    def __init__(self, root: Path, mapping: dict | None = None):
        self.root = root
        self.mapping = mapping or {}
        self._cache: dict[tuple, str | None] = {}

    def uri(self, key: str, max_side: int = 640, grayscale: bool = False) -> str | None:
        """Картинка по ключу из config/profile.json → images (или по пути). None, если файла нет."""
        rel = self.mapping.get(key, key)
        if isinstance(rel, dict):
            rel = rel.get("path")
        if not rel:
            return None
        cache_key = (rel, max_side, grayscale)
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load(self.root / rel, max_side, grayscale)
        return self._cache[cache_key]

    def align(self, key: str) -> str:
        """Какой частью картинка прижимается в рамке: xMidYMid (по центру), xMidYMin (верх) и т.п."""
        rel = self.mapping.get(key)
        return rel.get("align", "xMidYMid") if isinstance(rel, dict) else "xMidYMid"

    @staticmethod
    def _load(path: Path, max_side: int, grayscale: bool) -> str | None:
        if not path.is_file():
            print(f"[images] нет файла {path}", file=sys.stderr)
            return None
        if Image is None:
            mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
            return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            im = im.convert("L") if grayscale else im.convert("RGB")
            im.thumbnail((max_side, max_side), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=84, optimize=True, progressive=True)
        return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"
