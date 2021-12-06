import datetime
import importlib

import pytest

import settings

from faker import Faker
from starlette.datastructures import Secret

fake = Faker()


@pytest.fixture
def datetime_now():
    return datetime.datetime.now()


@pytest.fixture
def past_datetime():
    return fake.past_datetime()


@pytest.fixture
def fake_feed_type():
    return f'fake_feed_type_{fake.pyint()}'


@pytest.fixture
def fake_string():
    return fake.word()


@pytest.fixture
async def fake_token():
    return fake.word()


@pytest.fixture
def fake_url():
    return fake.uri()


@pytest.fixture
def import_user():
    import user

    yield user

    importlib.reload(user)


@pytest.fixture
def fake_credentials():
    username = Secret(fake.word())
    password = Secret(fake.word())

    return username, password


@pytest.fixture
def import_user_with_credential(import_user, fake_credentials):
    username, password = fake_credentials

    import_user._USERNAME = username
    import_user._PASSWORD = password

    return import_user, username, password


@pytest.fixture
def fake_token():  # noqa
    return fake.sha256()


@pytest.fixture
def fake_text_less_than_summary_limit():
    max_text_length = fake.pyint(
        settings.SUMMARY_TEXT_LIMIT // 2,
        settings.SUMMARY_TEXT_LIMIT
    )

    return fake.text(max_nb_chars=max_text_length)


@pytest.fixture
def fake_text_more_than_summary_limit():
    max_text_length = fake.pyint(
        settings.SUMMARY_TEXT_LIMIT + 1,
        settings.SUMMARY_TEXT_LIMIT * 2
    )

    return fake.text(max_nb_chars=max_text_length)


@pytest.fixture
def import_user_with_token(
        import_user,
        fake_token,
        datetime_now
        ):
    token = fake_token
    exp = (
        datetime_now + datetime.timedelta(settings.TOKEN_EXPIRATION_DELTA_DAYS)
    )

    import_user._TOKEN = token
    import_user._EXPIRATION = exp

    return import_user, token, exp


@pytest.fixture
def import_user_with_expired_token(
        import_user,
        fake_token,
        past_datetime
        ):
    token = fake_token
    exp = past_datetime

    import_user._TOKEN = token
    import_user._EXPIRATION = exp

    return import_user, token, exp
