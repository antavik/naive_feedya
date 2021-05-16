import random

from itertools import count
from typing import Tuple

from constants import NEWS, SPAM, TRUE_BOOL_STRINGS, FALSE_BOOL_STRINGS


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


def escape_single_quote(string: str) -> str:
    return string.replace('\'', '\'\'')


def color_pairs_randomizer() -> Tuple[str, str]:
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
    if string.lower() in TRUE_BOOL_STRINGS:
        return True
    elif string.lower() in FALSE_BOOL_STRINGS:
        return False
    else:
        raise ValueError('Unsupported value for boolean parameter')
