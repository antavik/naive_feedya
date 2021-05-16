from web.rendering import _format_datetime


def test_format_datetime__datetime__string(datetime_now):
    datetime_str = _format_datetime(datetime_now)

    assert isinstance(datetime_str, str)
