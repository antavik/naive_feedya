import secrets
import datetime

import settings

from typing import Tuple

from starlette.datastructures import Secret

USERNAME: Secret = settings.USERNAME
PASSWORD: Secret = settings.PASSWORD
_token: Secret = None
_expiration: datetime.datetime = None


def generate_token() -> Tuple[Secret, datetime.datetime]:
    global _token

    _token = Secret(secrets.token_hex())
    exp = _set_expiration_date()

    return _token, exp


def is_valid_credentials(username: str, password: str) -> bool:
    if username == str(USERNAME) and password == str(PASSWORD):
        is_valid = True
    else:
        is_valid = False

    return is_valid


def is_valid_token(token: str) -> bool:
    if str(_token) != token:
        is_valid = False
    elif _expiration <= datetime.datetime.now():
        is_valid = False
    else:
        is_valid = True

    return is_valid


def _set_expiration_date() -> datetime.datetime:
    global _expiration

    days_delta = datetime.timedelta(days=settings.TOKEN_EXPIRATION_DELTA_DAYS)
    _expiration = datetime.datetime.now() + days_delta

    return _expiration
