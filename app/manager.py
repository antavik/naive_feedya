import time
import logging

import httpx

from feeds import Feed, FEEDS_REGISTRY, FEEDS
from storage import FeedEntry, feed_entries_db 
from feed_classifier.classifier import classify, update_stats, reverse_stats
from feed_classifier.parser import parse
from web.rendering import render_html_page
from utils import trim_text


async def process_feed(feed: Feed) -> None:
    parsed_feed = await parse(feed)

    if not parsed_feed:
        return

    for entry in parsed_feed.entries:
        if not await feed_entries_db.exists(entry.link):
            published_timestamp = time.mktime(
                entry.get('published_parsed')
                or entry.get('updated_parsed')
                or time.localtime()
            )

            # TODO: Fix parsing
            published_summary = (
                '' if feed.skip_summary else entry.get('summary', '')
            )

            valid = await classify(entry.title, feed.language)

            await feed_entries_db.save(
                FeedEntry(
                    title=entry.title,
                    url=entry.link,
                    published_timestamp=published_timestamp,
                    feed=feed.title,
                    summary=trim_text(published_summary),
                    valid=valid,
                )
            )
    else:
        if parsed_feed.entries:
            logging.info('%s feed entries saved in DB', feed.title)
        else:
            logging.warning('Feed %s is empty', feed.title)


async def clean_feed_entries_db():
    removed = await feed_entries_db.remove_old()

    if removed:
        logging.info('Feed entries DB cleaned. Removed %d entries', removed)


async def get_current_weather():
    weather_service_url = (
        'https://wttr.in/Minsk?'
        'format=%l:+%c+%t+(feels+like+%f),+wind+%w,+%p+%P'
    )

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(weather_service_url)

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logging.error('Error while getting weather: %s', exc)

        weather = ''
    else:
        logging.info('Weather data recieved')

        weather = response.text

    return weather


async def get_news_page(last_hours: int) -> str:
    weather = await get_current_weather()

    feed_to_entries = {f: [] for f in FEEDS}
    news_entries = await feed_entries_db.fetch_last_news(last_hours)
    for entry in news_entries:
        feed = FEEDS_REGISTRY[entry.feed]
        feed_to_entries[feed].append(entry)

    html_page = render_html_page(feed_to_entries, 'news', last_hours, weather)

    return html_page


async def get_spam_page(last_hours: int) -> str:
    weather = await get_current_weather()

    feed_to_entries = {f: [] for f in FEEDS}
    spam_entries = await feed_entries_db.fetch_last_spam(last_hours)
    for entry in spam_entries:
        feed = FEEDS_REGISTRY[entry.feed]
        feed_to_entries[feed].append(entry)

    html_page = render_html_page(feed_to_entries, 'spam', last_hours, weather)

    return html_page


async def update_feed_classifier(feedback):
    if await feed_entries_db.is_classified(feedback.entry_url):
        updated_tokens = await reverse_stats(
            document=feedback.entry_title,
            label=feedback.entry_is_valid,
            language=feedback.entry_language
        )

        updated_tokens = bool(updated_tokens)
    else:
        updated_tokens, updated_docs = await update_stats(
            document=feedback.entry_title,
            label=feedback.entry_is_valid,
            language=feedback.entry_language
        )

        updated_tokens = bool(updated_tokens and updated_docs)

    if updated_tokens:
        await feed_entries_db.update_validity(
            url=feedback.entry_url,
            label=feedback.entry_is_valid
        )
