from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from manager import get_news_page, get_spam_page, update_feed_classifier

app = FastAPI(title='Naive Feedya')


class UserFeedback(BaseModel):
    entry_title: str
    entry_url: str
    entry_is_valid: bool
    entry_language: str


@app.get(
    '/feed/',
    response_class=HTMLResponse,
    summary='Get rendered news html page',
)
async def get_news():
    response = await get_news_page()

    return response


@app.get(
    '/feed/spam/',
    response_class=HTMLResponse,
    summary='Get rendered spam html page',
)
async def get_spam():
    response = await get_spam_page()

    return response


@app.put(
    '/feed/update',
    response_class=HTMLResponse,
    summary='Update feed classificator and entry label',
)
async def update(feedback: UserFeedback):
    await update_feed_classifier(feedback)

    return '✅' if feedback.entry_is_valid else '🚫'
