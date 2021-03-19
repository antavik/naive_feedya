import datetime
import random

import settings

from typing import Tuple, List, Dict

from jinja2 import Environment, FileSystemLoader
from jinja2.environment import Template

from feeds import Feed
from storage import FeedEntry


def color_randomizer() -> Tuple[str, str]:
    _support_color_pairs = (
        # background color, font color
        ('#fff3b0', '#b0bcff',),
        ('#25b8a9', '#b82534',),
        ('#b6ff1c', '#651cff',),
        ('#19f76d', '#f719a3',),
        ('#aec575', '#8c75c5',),
        ('#8dcf83', '#c583cf',),
        ('#6dd81b', '#861bd8',),
        ('#96ca98', '#814c7f',),
        ('#2a7e6c', '#7e2a3c',),
        ('#42e4e7', '#e74542',),
        ('#ffedbe', '#779dfe',),
    )

    return random.choice(_support_color_pairs)


def format_datetime(
        dt: datetime.datetime,
        format: str = settings.DT_TEMPLATE
    ) -> str:
    return dt.strftime(format)


def reverse_empty_feeds(
        feeds: Dict[Feed, List[FeedEntry]]
    ) -> List[Tuple[Feed, List[FeedEntry]]]:
    return sorted(
        feeds.items(),
        key=lambda x: 1 if x[1] else 0,
        reverse=True
    )


def _get_html_template() -> Template:
    environment = Environment(
        loader=FileSystemLoader(settings.TEMPLATES_PATH),
        autoescape=True
    )

    environment.filters['format_datetime'] = format_datetime
    environment.filters['reverse_empty_feeds'] = reverse_empty_feeds

    return environment.get_template(settings.TEMPLATE_FILENAME)


def render_html_page(
        feeds: Dict[Feed, List[FeedEntry]],
        entry_type: str,
        recent_hours: int
    ) -> str:
    template = _get_html_template()

    title_bg_color, title_font_color = color_randomizer()

    html_page = template.render(
        title_bg_color=title_bg_color,
        title_font_color=title_font_color,
        feed_datetime=datetime.datetime.now(),
        feeds=feeds,
        entry_type=entry_type,
        recent_hours=recent_hours
    )

    return html_page
