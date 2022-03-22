import random
import datetime

from itertools import count
from functools import lru_cache

from constants import NEWS, SPAM
from feeds import Feed
from storage.entities import FeedEntry


def trim_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text

    end_index = None

    ending = '...'
    limit_index = limit - 1
    trimmed_limit_index = limit_index - len(ending)

    for line, i in zip(text[limit_index::-1], count(limit_index, -1)):
        if (line == ' ' or i == '.') and i <= trimmed_limit_index:
            end_index = i - 1 if text[i-1] == '.' else i

            break

    text = text[:end_index] + ending

    return text


def color_pairs_randomizer() -> tuple[str, str]:
    _support_color_pairs = (
        # background color, font color
        ('#fff3b0', '#586acb',),
        ('#25b8a9', '#b82534',),
        ('#b6ff1c', '#651cff',),
        ('#19f76d', '#f719a3',),
        ('#8dcf83', '#c583cf',),
        ('#6dd81b', '#861bd8',),
        ('#96ca98', '#814c7f',),
        ('#71bdac', '#7e2a3c',),
        ('#42e4e7', '#e74542',),
        ('#ffedbe', '#779dfe',),
    )

    return random.choice(_support_color_pairs)


def label_by_feed_type(feed_type: str) -> bool:
    if feed_type == NEWS:
        label = True
    elif feed_type == SPAM:
        label = False
    else:
        raise ValueError('Unsupported value for feed type')

    return label


def str2bool(string: str) -> bool:
    true_bool_strings = {'yes', 'y', '1', 'true', 't'}
    false_bool_strings = {'no', 'n', '0', 'false', 'f', ''}

    if string.lower() in true_bool_strings:
        return True
    elif string.lower() in false_bool_strings:
        return False
    else:
        raise ValueError(
            f'Unsupported value for boolean parameter: '
            f'{type(string)} - {string}'
        )


def reverse_empty_feeds(
        feeds: dict[Feed, list[FeedEntry]]
) -> list[tuple[Feed, list[FeedEntry]]]:
    return sorted(
        feeds.items(),
        key=lambda x: bool(x[1]),
        reverse=True
    )


@lru_cache(maxsize=256)
def format_datetime(dt: datetime.datetime, template: str) -> str:
    return dt.strftime(template)


@lru_cache(maxsize=256)
def escape_single_quote(s: str) -> str:
    return s.replace('\'', '\'\'')


@lru_cache(maxsize=256)
def escape_double_quotes(s: str) -> str:
    return s.replace('"', r'\"')
