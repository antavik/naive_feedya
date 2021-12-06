import secrets
import datetime

import settings

from typing import Tuple

from starlette.datastructures import Secret

_USERNAME = settings.USERNAME
_PASSWORD = settings.PASSWORD
_TOKEN: Secret = None
_EXPIRATION: datetime.datetime = None


def generate_token() -> Tuple[Secret, datetime.datetime]:
    global _TOKEN, _EXPIRATION

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


def _get_expiration_date() -> datetime.datetime:
    days_delta = datetime.timedelta(days=settings.TOKEN_EXPIRATION_DELTA_DAYS)
    expiration = datetime.datetime.now() + days_delta

    return expiration
