import typing as t

import settings
import user

from pydantic import BaseModel
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestFormStrict,
)
from fastapi.middleware.gzip import GZipMiddleware
from starlette.responses import RedirectResponse

from feeds import FEEDS, FEEDS_REGISTRY
from manager import (
    get_base_page,
    get_tab_sub_page,
    update_feed_classifier,
    get_login_sub_page,
)
from constants import EntryType
from .exceptions import (
    InvalidCredentials,
    FeedTypeNotFound,
    InternalServerError,
)

APP = FastAPI(title=settings.API_NAME, debug=settings.DEV_MODE)
APP.mount(
    '/static',
    StaticFiles(directory=str(settings.STATIC_PATH)),
    name='static'
)

APP.add_middleware(GZipMiddleware, minimum_size=300)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/oauth/token', auto_error=False)


class UserFeedback(BaseModel):
    entry_title: str
    entry_url: str
    entry_is_valid: bool
    entry_language: str


@APP.get(
    '/oauth/login',
    response_class=HTMLResponse,
    summary='Get login sub-page'
)
async def get_login_page():
    response = await get_login_sub_page()

    return response


@APP.put(
    '/oauth/token',
    summary='Put credentials'
)
async def login_user(form_data: OAuth2PasswordRequestFormStrict = Depends()):
    if not user.is_valid_credentials(form_data.username, form_data.password):
        raise InvalidCredentials

    token, _ = user.generate_token()
    response = {'access_token': str(token), 'token_type': 'bearer'}

    return response


@APP.get(
    '/{feed_type}',
    response_class=HTMLResponse,
    summary='Get base html page'
)
async def get_news_page(feed_type: str):
    try:
        feed_type = EntryType[feed_type.upper()]
    except KeyError:
        raise FeedTypeNotFound from None

    return await get_base_page(feed_type=feed_type)


@APP.get(
    '/{feed_type}/tab/',
    response_class=HTMLResponse | RedirectResponse,
    summary='Get feed sub-page or redirect to login sub-page'
)
async def get_news_tab_sub_page(
        feed_type: str,
        last_hours: int,
        token: t.Optional[str] = Depends(oauth2_scheme)
):
    if token is None or not user.is_valid_token(token):
        return RedirectResponse(
            url=settings.PATH_PREFIX + APP.url_path_for('get_login_page'),
            headers={'WWW-Authenticate': 'Bearer'}
        )

    try:
        feed_type = EntryType[feed_type.upper()]
    except KeyError:
        raise FeedTypeNotFound from None

    content = await get_tab_sub_page(
        FEEDS, FEEDS_REGISTRY, feed_type, last_hours
    )

    return HTMLResponse(
        content=content,
        headers={'WWW-Authenticate': 'Bearer'}
    )


@APP.put(
    '/api/entry',
    response_class=HTMLResponse,
    summary='Feed entries api'
)
async def update(
        feedback: UserFeedback,
        token: t.Optional[str] = Depends(oauth2_scheme)
):
    if token is None or not user.is_valid_token(token):
        return RedirectResponse(
            url=settings.PATH_PREFIX + APP.url_path_for('get_login_page'),
            headers={'WWW-Authenticate': 'Bearer'}
        )

    content = await update_feed_classifier(feedback)
    if content is None:
        raise InternalServerError

    return HTMLResponse(
        content=content,
        headers={'WWW-Authenticate': 'Bearer'}
    )


@APP.get(
    '/ping',
    response_class=PlainTextResponse,
    summary='Ping'
)
async def ping():
    return 'Pong'
