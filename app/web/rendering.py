import datetime

import settings
import utils

from typing import List, Dict, Tuple

from jinja2 import Environment, FileSystemLoader

from feeds import Feed
from storage.entities import FeedEntry

_ENVIRONMENT = Environment(
    loader=FileSystemLoader(settings.TEMPLATES_PATH),
    autoescape=True,
    enable_async=True
)


def _format_datetime(dt: datetime.datetime) -> str:
    return dt.strftime(settings.DT_TEMPLATE)


def _reverse_empty_feeds(
        feeds: Dict[Feed, List[FeedEntry]]
        ) -> List[Tuple[Feed, List[FeedEntry]]]:
    return sorted(
        feeds.items(),
        key=lambda x: bool(x[1]),
        reverse=True
    )


def _escape_double_quotes(s: str) -> str:
    return s.replace('"', r'\"')


_ENVIRONMENT.filters['format_datetime'] = _format_datetime
_ENVIRONMENT.filters['reverse_empty_feeds'] = _reverse_empty_feeds
_ENVIRONMENT.filters['escape_double_quotes'] = _escape_double_quotes


async def render_base_page(entry_type: str) -> str:
    tamplate = _ENVIRONMENT.get_template(settings.BASE_TEMPLATE_FILENAME)

    title_bg_color, title_font_color = utils.color_pairs_randomizer()

    html_page = await tamplate.render_async(
        title_bg_color=title_bg_color,
        title_font_color=title_font_color,
        feed_datetime=datetime.datetime.now(),
        entry_type=entry_type
    )

    return html_page


async def render_tab_sub_page(
        entry_type: str,
        last_hours: int,
        feeds: Dict[Feed, List[FeedEntry]]
        ) -> str:
    tamplate = _ENVIRONMENT.get_template(settings.TAB_TEMPLATE_FILENAME)

    html_page = await tamplate.render_async(
        entry_type=entry_type,
        last_hours=last_hours,
        feeds=feeds
    )

    return html_page


async def render_login_sub_page() -> str:
    template = _ENVIRONMENT.get_template(settings.LOGIN_TEMPLATE_FILENAME)

    html_page = await template.render_async()

    return html_page
