import datetime

import settings
import utils

from typing import List, Dict

from jinja2 import Environment, FileSystemLoader
from jinja2.environment import Template

from feeds import Feed
from storage.entities import FeedEntry


def _get_html_template() -> Template:
    environment = Environment(
        loader=FileSystemLoader(settings.TEMPLATES_PATH),
        autoescape=True,
        enable_async=True
    )

    environment.filters['format_datetime'] = utils.format_datetime
    environment.filters['reverse_empty_feeds'] = utils.reverse_empty_feeds

    return environment.get_template(settings.TEMPLATE_FILENAME)


TEMPLATE = _get_html_template()


async def render_html_page(
        feeds: Dict[Feed, List[FeedEntry]],
        entry_type: str,
        recent_hours: int,
        weather: str
        ) -> str:
    title_bg_color, title_font_color = utils.color_pairs_randomizer()

    html_page = await TEMPLATE.render_async(
        title_bg_color=title_bg_color,
        title_font_color=title_font_color,
        feed_datetime=datetime.datetime.now(),
        feeds=feeds,
        entry_type=entry_type,
        recent_hours=recent_hours,
        weather=weather
    )

    return html_page
