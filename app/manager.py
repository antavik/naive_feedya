import time
import logging

from typing import List
from collections.abc import Iterable

import httpx

from feeds import Feed, FEEDS_REGISTRY, FEEDS
from storage import FeedEntry, feed_entries_db
from feed_classifier.classifier import classify, update_stats, reverse_stats
from feed_classifier.parser import parse
from web.rendering import render_html_page
from utils import trim_text, label_by_feed_type


async def _prepare_feed_entries(
        feed: Feed,
        new_parsed_entries: Iterable[str]
        ) -> List[FeedEntry]:
    feed_entries = []

    for entry in new_parsed_entries:
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

        feed_entries.append(
            FeedEntry(
                title=entry.title,
                url=entry.link,
                published_timestamp=published_timestamp,
                feed=feed.title,
                summary=trim_text(published_summary),
                valid=valid,
            )
        )

    return feed_entries


async def process_feed(feed: Feed) -> None:
    parsed_feed_entries = await parse(feed)

    if not parsed_feed_entries:
        logging.warning('Feed %s is empty', feed.title)

        return

    exist_urls = await feed_entries_db.exist_urls(
        (e.link for e in parsed_feed_entries)
    )

    if sorted(exist_urls) == sorted(e.link for e in parsed_feed_entries):
        logging.info('All entries from %s feed exist', feed.title)

        return

    entries_to_save = await _prepare_feed_entries(
        feed,
        (e for e in parsed_feed_entries if e.link not in exist_urls)
    )

    await feed_entries_db.save_many(entries_to_save)


async def clean_feed_entries_db():
    removed = await feed_entries_db.remove_old()

    if removed:
        logging.info('Feed entries DB cleaned. Removed %d entries', removed)


async def get_current_weather() -> str:
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


async def get_feed_page(feed_type: str, last_hours: int) -> str:
    weather = await get_current_weather()

    label = label_by_feed_type(feed_type)

    feed_to_entries = {f: [] for f in FEEDS}
    news_entries = await feed_entries_db.fetch_last_entries(
        feeds=(f.title for f in FEEDS),
        valid=label,
        hours_delta=last_hours
    )
    for entry in news_entries:
        feed = FEEDS_REGISTRY[entry.feed]
        feed_to_entries[feed].append(entry)

    html_page = await render_html_page(
        feed_to_entries,
        feed_type,
        last_hours,
        weather
    )

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
