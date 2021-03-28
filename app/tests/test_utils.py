import pytest

import settings

from utils import trim_text, label_by_feed_type


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


def test_label_by_feed_type__news__true():
    assert label_by_feed_type(settings.NEWS)


def test_label_by_feed_type__spam__false():
    assert not label_by_feed_type(settings.SPAM)


def test_label_by_feed_type__invalid_type__exception(fake_feed_type):
    with pytest.raises(Exception):
        label_by_feed_type(fake_feed_type)
