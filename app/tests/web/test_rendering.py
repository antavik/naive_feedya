import re

from web.rendering import color_randomizer, format_datetime


def test_colot_randomizer__no_input__tuple_hex_color():
    pattern = re.compile(r'^#[a-zA-Z0-9]{6}$')  # hex code pattern

    colors = color_randomizer()
    background_color, font_color = colors

    assert pattern.match(background_color) and pattern.match(font_color)


def test_format_datetime__datetime__string(datetime_now):
    datetime_str = format_datetime(datetime_now)

    assert isinstance(datetime_str, str)
