"""☀️ Дневная сакура: небо, облака, зелёный холм, котики, пруд с карпами кои."""

from .. import anime_list, quote as quote_card, scenery, status_window


def header(cfg, ctx):
    return scenery.build_header(cfg, ctx.fonts)


def divider(ctx):
    return scenery.build_divider()


def footer(cfg, ctx):
    return scenery.build_footer(cfg, ctx.fonts)


def status(stats, derived, cfg, ctx, exclude):
    return status_window.build(stats, derived, cfg, ctx.fonts, exclude)


def quote(quotes, ctx):
    return quote_card.build(quotes, ctx.fonts)


def anime(data, username, ctx, max_items):
    return anime_list.build(data, username, ctx.fonts, max_items)
