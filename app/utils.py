import random
import typing as t
import hashlib

from itertools import count
from functools import lru_cache


def trim_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text

    end_index = None

    ending = '...'
    limit_index = limit - len(ending) - 1

    for i, ch in zip(count(limit_index, -1), text[limit_index::-1]):
        if ch == ' ':
            end_index = i

            break
        elif ch == '.':
            end_index = i - 1

            break

    return text[:end_index] + ending


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


def to_bool(value: t.Any) -> bool:
    if not isinstance(value, str):
        value = str(value)

    true_bool_strings = {'yes', 'y', '1', 'true', 't'}
    false_bool_strings = {'no', 'n', '0', 'false', 'f', ''}

    string_lower = value.lower()

    if string_lower in true_bool_strings:
        return True
    elif string_lower in false_bool_strings:
        return False
    else:
        raise ValueError(
            f'Unsupported value for boolean parameter: '
            f'{type(value)} - {value}'
        )


@lru_cache(maxsize=64)
def hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


@lru_cache(maxsize=1024)
def escape_single_quote(s: str) -> str:
    return s.replace('\'', '\'\'')


@lru_cache(maxsize=1024)
def escape_double_quotes(s: str) -> str:
    return s.replace('"', r'\"')


@lru_cache(maxsize=64)
def lower(s: str) -> str:
    return s.lower()


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)  # noqa

        return cls._instances[cls]
