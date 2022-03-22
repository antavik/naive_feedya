import re

import pytest

import settings

from utils import (
    trim_text,
    escape_single_quote,
    color_pairs_randomizer,
    label_by_feed_type,
    str2bool,
    format_datetime,
)
from constants import NEWS, SPAM


def test_trim_text__text_less_than_summary_limit__same_text(
        fake_text_less_than_summary_limit
):
    text = trim_text(
        fake_text_less_than_summary_limit,
        settings.SUMMARY_TEXT_LIMIT
    )

    assert len(text) <= settings.SUMMARY_TEXT_LIMIT and text[-1] == '.'


def test_trim_text__text_more_than_summary_limit__trimmed_text(
        fake_text_more_than_summary_limit
):
    text = trim_text(
        fake_text_more_than_summary_limit,
        settings.SUMMARY_TEXT_LIMIT
    )

    assert len(text) <= settings.SUMMARY_TEXT_LIMIT and text[-1] == '.'


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


def test_label_by_feed_type__news__true():
    assert label_by_feed_type(NEWS)


def test_label_by_feed_type__spam__false():
    assert not label_by_feed_type(SPAM)


def test_label_by_feed_type__invalid_type__exception(fake_feed_type):
    with pytest.raises(ValueError):
        label_by_feed_type(fake_feed_type)


def test_str2bool__valid_true_str__bool_true():
    true_bool_strings = ['yes', 'y', '1', 'true', 't']
    upper_true_bool_strings = [s.upper() for s in true_bool_strings]

    for bool_str in true_bool_strings + upper_true_bool_strings:
        assert str2bool(bool_str) is True


def test_str2bool__valid_false_str__bool_false():
    false_bool_strings = ['no', 'n', '0', 'false', 'f', '']
    upper_false_bool_strings = [s.upper() for s in false_bool_strings]

    for bool_str in false_bool_strings + upper_false_bool_strings:
        assert str2bool(bool_str) is False


def test_str2bool__valid_invalid_str__exception():
    invalid_bool_str = 'truth'

    with pytest.raises(ValueError):
        str2bool(invalid_bool_str)
