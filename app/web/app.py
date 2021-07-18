import settings
import user

from typing import Optional, Union

from pydantic import BaseModel
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestFormStrict,
)
from starlette.responses import RedirectResponse

from manager import (
    get_base_page,
    get_tab_sub_page,
    update_feed_classifier,
    get_login_sub_page,
)
from constants import NEWS, SPAM
from .exceptions import InvalidCredentialsException, EntryURLNotFoundException

APP = FastAPI(title=settings.API_NAME)
APP.mount(
    '/static',
    StaticFiles(directory=str(settings.STATIC_PATH)),
    name='static'
)

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
        raise InvalidCredentialsException

    token, _ = user.generate_token()
    response = {'access_token': str(token), 'token_type': 'bearer'}

    return response


@APP.get(
    '/news',
    response_class=HTMLResponse,
    summary='Get rendered news html page'
)
async def get_news_page():
    response = await get_base_page(feed_type=NEWS)

    return response


@APP.get(
    '/news/tab/',
    response_class=Union[HTMLResponse, RedirectResponse],
    summary='Get news sub-page for main feed page or redirect login sub-page'
)
async def get_news_tab_sub_page(
        last_hours: int,
        token: Optional[str] = Depends(oauth2_scheme)
        ):
    if token is not None and user.is_valid_token(token):
        content = await get_tab_sub_page(NEWS, last_hours)
        response = HTMLResponse(
            content=content,
            headers={'WWW-Authenticate': 'Bearer'}
        )
    else:
        login_page_url = '/feed' + APP.url_path_for('get_login_page')
        response = RedirectResponse(
            url=login_page_url,
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return response


@APP.get(
    '/spam',
    response_class=HTMLResponse,
    summary='Get rendered spam html page'
)
async def get_spam_page():
    response = await get_base_page(feed_type=SPAM)

    return response


@APP.get(
    '/spam/tab/',
    response_class=HTMLResponse,
    summary='Get spam sub-page for main feed page or redirect login sub-page'
)
async def get_spam_tab_sub_page(
        last_hours: int,
        token: Optional[str] = Depends(oauth2_scheme)
        ):
    if token is not None and user.is_valid_token(token):
        content = await get_tab_sub_page(SPAM, last_hours)
        response = HTMLResponse(
            content=content,
            headers={'WWW-Authenticate': 'Bearer'}
        )
    else:
        login_page_url = '/feed' + APP.url_path_for('get_login_page')
        response = RedirectResponse(
            url=login_page_url,
            headers={
                'WWW-Authenticate': 'Bearer',
            }
        )

    return response


@APP.put(
    '/update',
    response_class=HTMLResponse,
    summary='Update feed classificator and entry label'
)
async def update(
        feedback: UserFeedback,
        token: Optional[str] = Depends(oauth2_scheme)
        ):
    if token is not None and user.is_valid_token(token):
        if await update_feed_classifier(feedback) is None:
            raise EntryURLNotFoundException

        content = '✅' if feedback.entry_is_valid else '🚫'
        response = f'<span>{content}</span>'
    else:
        get_login_page_url = APP.url_path_for('get_login_page')
        response = RedirectResponse(
            url=get_login_page_url,
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return response
