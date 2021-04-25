import settings

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from manager import get_feed_page, update_feed_classifier

app = FastAPI(title='Naive Feedya')


class UserFeedback(BaseModel):
    entry_title: str
    entry_url: str
    entry_is_valid: bool
    entry_language: str


@app.get(
    '/feed/news/',
    response_class=HTMLResponse,
    summary='Get rendered news html page',
)
async def get_news(last_hours: int = settings.RECENT_FEED_ENTRIES_HOURS):
    response = await get_feed_page(settings.NEWS, last_hours)

    return response


@app.get(
    '/feed/spam/',
    response_class=HTMLResponse,
    summary='Get rendered spam html page',
)
async def get_spam(last_hours: int = settings.RECENT_FEED_ENTRIES_HOURS):
    response = await get_feed_page(settings.SPAM, last_hours)

    return response


@app.put(
    '/feed/update',
    response_class=HTMLResponse,
    summary='Update feed classificator and entry label',
)
async def update(feedback: UserFeedback):
    if await update_feed_classifier(feedback) is None:
        raise HTTPException(status_code=404, detail='Feed entry URL not found')

    return '✅' if feedback.entry_is_valid else '🚫'
