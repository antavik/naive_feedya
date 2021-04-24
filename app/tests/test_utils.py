import re
import pytest

import settings

from utils import (
    trim_text,
    escape_single_quote,
    color_pairs_randomizer,
    format_datetime,
    label_by_feed_type,
)


def test_trim_text__text_less_than_summary_limit__same_text(
        fake_text_less_than_summary_limit
        ):
    text = trim_text(fake_text_less_than_summary_limit)

    assert len(text) <= settings.SUMMARY_LIMIT and text[-1] == '.'


def test_trim_text__text_more_than_summary_limit__trimmed_text(
        fake_text_more_than_summary_limit
        ):
    text = trim_text(fake_text_more_than_summary_limit)

    assert len(text) <= settings.SUMMARY_LIMIT and text[-1] == '.'


def test_escape_single_quote__string__string(fake_string):
    text_with_single_quotes = fake_string + "'"
    text_with_double_quotes = fake_string + "''"

    assert (
        escape_single_quote(text_with_single_quotes) == text_with_double_quotes
    )


def test_colot_randomizer__no_input__tuple_hex_color():
    pattern = re.compile(r'^#[a-zA-Z0-9]{6}$')  # hex code pattern

    colors = color_pairs_randomizer()
    background_color, font_color = colors

    assert pattern.match(background_color) and pattern.match(font_color)


def test_format_datetime__datetime__string(datetime_now):
    datetime_str = format_datetime(datetime_now)

    assert isinstance(datetime_str, str)


def test_label_by_feed_type__news__true():
    assert label_by_feed_type(settings.NEWS)


def test_label_by_feed_type__spam__false():
    assert not label_by_feed_type(settings.SPAM)


def test_label_by_feed_type__invalid_type__exception(fake_feed_type):
    with pytest.raises(Exception):
        label_by_feed_type(fake_feed_type)
