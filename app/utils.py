import sys
import random
import datetime

import settings
import parser

from itertools import count
from typing import Tuple, Dict, List

from feeds import Feed
from storage.entities import FeedEntry


def configure_logging():
    from logging import Formatter, getLogger, INFO, DEBUG, StreamHandler

    logger = getLogger()

    handler = StreamHandler(sys.stdout)
    formatter = Formatter(settings.LOGGING_FORMAT, settings.LOGGING_DT_FORMAT)

    handler.setLevel(INFO)
    handler.setFormatter(formatter)

    logger.setLevel(DEBUG)
    logger.addHandler(handler)


def trim_text(text: str) -> str:
    if len(text) <= settings.SUMMARY_LIMIT:
        return text

    end_index = None

    ending = '...'
    limit_index = settings.SUMMARY_LIMIT - 1
    trimmed_limit_index = limit_index - len(ending)

    for line, i in zip(text[limit_index::-1], count(limit_index, -1)):
        if (line == ' ' or i == '.') and i <= trimmed_limit_index:
            end_index = i - 1 if text[i-1] == '.' else i

            break

    text = text[:end_index] + ending

    return text


def escape_single_quote(string: str) -> str:
    return string.replace('\'', '\'\'')


def color_pairs_randomizer() -> Tuple[str, str]:
    _support_color_pairs = (
        # background color, font color
        ('#fff3b0', '#586acb',),
        ('#25b8a9', '#b82534',),
        ('#b6ff1c', '#651cff',),
        ('#19f76d', '#f719a3',),
        ('#aec575', '#8c75c5',),
        ('#8dcf83', '#c583cf',),
        ('#6dd81b', '#861bd8',),
        ('#96ca98', '#814c7f',),
        ('#71bdac', '#7e2a3c',),
        ('#42e4e7', '#e74542',),
        ('#ffedbe', '#779dfe',),
    )

    return random.choice(_support_color_pairs)


def format_datetime(
        dt: datetime.datetime,
        format: str = settings.DT_TEMPLATE
        ) -> str:
    return dt.strftime(format)


def label_by_feed_type(feed_type: str) -> bool:
    if feed_type == settings.NEWS:
        label = True
    elif feed_type == settings.SPAM:
        label = False
    else:
        raise Exception

    return label


def reverse_empty_feeds(
        feeds: Dict[Feed, List[FeedEntry]]
        ) -> List[Tuple[Feed, List[FeedEntry]]]:
    return sorted(
        feeds.items(),
        key=lambda x: bool(x[1]),
        reverse=True
    )


def feed_entries_threshold_timestamp(
        days: int = settings.FEED_ENTRIES_DAYS_THRESHOLD
        ) -> float:
    threshold_datetime = datetime.datetime.now() - datetime.timedelta(days=days)  # noqa

    return threshold_datetime.timestamp()


def under_date_threshold(
        entry: parser.EntryProxy
        ) -> bool:
    threshold_timestamp = feed_entries_threshold_timestamp()

    if entry.published_date and entry.published_date < threshold_timestamp:
        result = False
    else:
        result = True

    return result
