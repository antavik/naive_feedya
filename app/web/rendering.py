import datetime

import settings
import constants as const
import utils

from jinja2 import Environment, FileSystemLoader

from feeds import Feed
from storage.entities import FeedEntry


_ENVIRONMENT = Environment(
    loader=FileSystemLoader(settings.TEMPLATES_PATH),
    autoescape=True,
    enable_async=True
)


def _format_datetime(
        dt: datetime.datetime,
        template: str = settings.DT_TEMPLATE
) -> str:
    return dt.strftime(template)


def _reverse_empty_feeds(
        feeds: dict[Feed, list[FeedEntry]]
) -> list[tuple[Feed, list[FeedEntry]]]:
    return sorted(
        feeds.items(),
        key=lambda x: bool(x[1]),
        reverse=True
    )


_ENVIRONMENT.filters['format_datetime'] = _format_datetime
_ENVIRONMENT.filters['reverse_empty_feeds'] = _reverse_empty_feeds
_ENVIRONMENT.filters['escape_double_quotes'] = utils.escape_double_quotes
_ENVIRONMENT.globals['path_prefix'] = settings.PATH_PREFIX


async def render_base_page(feed_type: const.EntryType) -> str:
    template = _ENVIRONMENT.get_template(settings.BASE_TEMPLATE_FILENAME)

    title_bg_color, title_font_color = utils.color_pairs_randomizer()

    html_page = await template.render_async(
        title_bg_color=title_bg_color,
        title_font_color=title_font_color,
        feed_datetime=datetime.datetime.now(),
        feed_type=utils.lower(feed_type.name),
        language=settings.APP_LANG.value.capitalize()
    )

    return html_page


async def render_tab_sub_page(
        feed_type: const.EntryType,
        last_hours: int,
        feeds: dict[Feed, list[FeedEntry]]
) -> str:
    template = _ENVIRONMENT.get_template(settings.TAB_TEMPLATE_FILENAME)

    html_page = await template.render_async(
        entry_type=utils.lower(feed_type.name),
        opposite_type=utils.lower(const.EntryType(not feed_type).name),
        last_hours=last_hours,
        feeds=feeds
    )

    return html_page


async def render_login_sub_page() -> str:
    template = _ENVIRONMENT.get_template(settings.LOGIN_TEMPLATE_FILENAME)

    html_page = await template.render_async()

    return html_page
