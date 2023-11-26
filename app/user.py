import secrets
import datetime

import settings
import constants

from starlette.datastructures import Secret

_USERNAME = settings.USERNAME
_PASSWORD = settings.PASSWORD


def _get_expiration_date() -> datetime.datetime:
    return datetime.datetime.now() + datetime.timedelta(days=settings.TOKEN_EXPIRATION_DELTA_DAYS)  # noqa


if settings.DEV_MODE:
    _TOKEN: Secret = Secret(constants.DEV_AUTH_TOKEN)
    _EXPIRATION: datetime.datetime = _get_expiration_date()
else:
    _TOKEN: Secret = None
    _EXPIRATION: datetime.datetime = None


def generate_token() -> tuple[Secret, datetime.datetime]:
    global _TOKEN, _EXPIRATION

    if settings.DEV_MODE:
        return _TOKEN, _EXPIRATION

    _TOKEN = Secret(secrets.token_hex())
    _EXPIRATION = _get_expiration_date()

    return _TOKEN, _EXPIRATION


def is_valid_credentials(username: str, password: str) -> bool:
    if (
        username == str(_USERNAME)
        and password == str(_PASSWORD)
    ):
        is_valid = True
    else:
        is_valid = False

    return is_valid


def is_valid_token(token: str) -> bool:
    if str(_TOKEN) != token:
        is_valid = False
    elif _EXPIRATION <= datetime.datetime.now():
        is_valid = False
    else:
        is_valid = True

    return is_valid
