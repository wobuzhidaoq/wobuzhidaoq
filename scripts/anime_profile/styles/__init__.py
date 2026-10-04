"""Стили профиля. Каждый стиль — модуль с одинаковым набором функций:

header(cfg, ctx), divider(ctx), footer(cfg, ctx), status(stats, derived, cfg, ctx, exclude),
quote(quotes, ctx, pinned), anime(data, username, ctx, max_items),
views_caption(cfg, ctx).
"""

import importlib
from dataclasses import dataclass

from ..fonts import FontEmbedder
from ..images import ImageLoader

STYLES = {"sakura-day": "sakura_day", "manga": "manga"}


@dataclass
class Ctx:
    fonts: FontEmbedder
    images: ImageLoader


def load(name: str):
    if name not in STYLES:
        raise ValueError(f"неизвестный стиль {name!r}, есть: {', '.join(STYLES)}")
    return importlib.import_module(f".{STYLES[name]}", __name__)
