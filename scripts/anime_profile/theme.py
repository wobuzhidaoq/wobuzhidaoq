"""Общая палитра «ночная сакура» для всех карточек."""

BG_DEEP = "#0a0820"
BG = "#120d2b"
BG_2 = "#1d1145"
BG_3 = "#2a1747"

PINK = "#ff8fc7"
PINK_LIGHT = "#ffd1e8"
PINK_DEEP = "#ff5fa2"
LAVENDER = "#b9a6ff"
PURPLE = "#7c5cff"
CYAN = "#7de3ff"
GOLD = "#ffe9a8"
TEXT = "#f4ecff"
MUTED = "#a99bc9"

FONT_FAMILY = "M PLUS Rounded 1c"
FONT_STACK = (
    "'M PLUS Rounded 1c', 'Hiragino Maru Gothic ProN', 'Yu Gothic UI', "
    "'Noto Sans JP', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
)

# Отключаем анимации у тех, кто попросил систему «поменьше движения».
REDUCED_MOTION_CSS = (
    "@media (prefers-reduced-motion: reduce) "
    "{ * { animation: none !important; } }"
)
