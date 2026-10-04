"""Общая палитра «дневная сакура»: голубое небо, розовые лепестки, светлые карточки."""

# Тексты
INK = "#4a2040"       # основной текст (тёмная слива — читается на светлом)
INK_SOFT = "#8e5a7c"  # подписи
ACCENT = "#ff4f9a"    # главный розовый акцент
ACCENT_2 = "#2a86cf"  # второй акцент: небесно-голубой для служебных надписей
GOLD = "#e8930c"

# Заливки
PINK = "#ff8fc7"
PINK_LIGHT = "#ffd1e6"
LILAC = "#b18cff"
SKY = "#5bb8f5"
LEAF = "#6cc070"
WHITE = "#ffffff"

# Карточки
CARD_TOP = "#fffbfd"
CARD_BOTTOM = "#ffeaf3"
TRACK = "#ffe0ee"       # фон полосок прогресса
CELL = "#fff3f8"
CELL_STROKE = "#ffc6de"

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
