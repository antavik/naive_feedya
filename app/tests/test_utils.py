import settings

from utils import trim_text


def test_trim_text__text_less_than_summary_limit__same_text(
        fake_text_less_than_summary_limit
    ):
    text = trim_text(fake_text_less_than_summary_limit)

    assert len(text) <= settings.SUMMARY_LIMIT and text[-1] == '.'


def test_trim_text__text_more_than_summary_limit__trimmed_text(
        fake_text_more_than_summary_limit
    ):
    print(fake_text_more_than_summary_limit, len(fake_text_more_than_summary_limit))
    text = trim_text(fake_text_more_than_summary_limit)
    print(text, len(text))

    assert len(text) <= settings.SUMMARY_LIMIT and text[-1] == '.'
