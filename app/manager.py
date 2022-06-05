import logging
import asyncio
import random
import datetime
import hashlib
import gzip
import typing as t

import clipper
import utils
import settings

from feedparser import FeedParserDict

from feeds import Feed
from parser import parse, EntryProxy
from scraper import Scraper
from constants import EntryType
from storage import feed_entries_db, stats_db
from web import render_base_page, render_tab_sub_page, render_login_sub_page
from storage.entities import FeedEntry
from feed_classifier.classifier import classify, update_stats, reverse_stats

log = logging.getLogger(settings.LOGGER_NAME)


async def process_feed(feed: Feed, scraper: Scraper):
    await asyncio.sleep(random.randint(*settings.FEED_REFRESH_JITTER_TIME_MINUTES) * 60)  # noqa

    feed_data, scraped_dt = await scraper.get(feed)
    if not feed_data:
        log.warning('Feed %s is empty', feed.title)

        return

    parsed_feed_entries = parse(feed_data)
    filtered_entries = await filter_feed_entries(parsed_feed_entries)

    entries_to_save = await prepare_feed_entries(
        feed, filtered_entries, scraped_dt
    )

    await feed_entries_db.save_many(entries_to_save)


async def filter_feed_entries(
        parsed_feed_entries: list[EntryProxy]
) -> t.Generator[EntryProxy, None, None]:
    fresh_urls = {
        entry.url
        for entry in parsed_feed_entries
        if entry.under_date_threshold
    }

    exist_urls = await feed_entries_db.filter_exist_urls(fresh_urls)

    new_entries = (
        entry
        for entry in parsed_feed_entries
        if entry.url in fresh_urls and entry.url not in exist_urls
    )

    return new_entries


async def prepare_feed_entries(
        feed: Feed,
        new_parsed_entries: t.Iterable[FeedParserDict],
        parsed_dt: datetime.datetime
) -> list[FeedEntry]:
    feed_entries = []
    parsed_timestamp = parsed_dt.timestamp()

    for entry in new_parsed_entries:
        published_timestamp = entry.published_timestamp or parsed_timestamp

        published_summary = '' if feed.skip_summary else entry.summary

        valid = await classify(entry.title, feed.language)

        feed_entries.append(
            FeedEntry(
                title=entry.title,
                url=entry.url,
                published_timestamp=published_timestamp,
                parsed_timestamp=parsed_timestamp,
                feed=feed.title,
                summary=utils.trim_text(
                    text=published_summary,
                    limit=settings.SUMMARY_TEXT_LIMIT
                ),
                valid=valid,
            )
        )

    return feed_entries


async def clean_feed_entries_db():
    removed = await feed_entries_db.remove_old()

    if removed:
        log.info('Feed entries DB cleaned. Removed %d entries', removed)


async def get_base_page(feed_type: EntryType) -> str:
    html_page = await render_base_page(feed_type)

    return html_page


async def get_tab_sub_page(
        feeds: list[Feed],
        feed_registry: dict[str, Feed],
        feed_type: EntryType,
        last_hours: int
) -> str:
    label = bool(feed_type)
    feed_to_entries: dict[Feed, list] = {f: [] for f in feeds}

    news_entries = await feed_entries_db.fetch_last_entries(
        feeds=feed_registry.keys(),
        valid=label,
        hours_delta=last_hours
    )

    for entry in news_entries:
        feed = feed_registry[entry.feed]
        feed_to_entries[feed].append(entry)

    html_page = await render_tab_sub_page(
        feed_type,
        last_hours,
        feed_to_entries
    )

    return html_page


async def get_login_sub_page() -> str:
    html_page = await render_login_sub_page()

    return html_page


async def update_feed_classifier(feedback: 'UserFeedback') -> bool | None:  # TODO: make typing correct  # noqa
    entry_classified = await feed_entries_db.is_classified(feedback.entry_url)

    if entry_classified is None:
        log.warning('URL doesn\'t exist %s', feedback.entry_url)

        return

    if entry_classified:
        updated_tokens = await reverse_stats(
            document=feedback.entry_title,
            label=feedback.entry_is_valid,
            language=feedback.entry_language
        )

        updated = bool(updated_tokens)
    else:
        updated_tokens, updated_docs = await update_stats(
            document=feedback.entry_title,
            label=feedback.entry_is_valid,
            language=feedback.entry_language
        )

        updated = bool(updated_tokens and updated_docs)

    if updated:
        await feed_entries_db.update_validity(
            url=feedback.entry_url,
            label=feedback.entry_is_valid
        )

    return updated


async def archive_classified_entities(clipper_client: clipper.Client):
    entries = await feed_entries_db.fetch_unarchived_valid_classified_entries()

    for e in entries:
        # can't use async tasks 'cause lambda starts glitching
        await archive_entry(e, clipper_client)


async def archive_entry(entry: FeedEntry, clipper_client: clipper.Client):
    try:
        article = await clipper_client.make_readable(entry.url)
    except clipper.ClippingError as exc:
        entry.archive = str(exc)
    else:
        filename = hashlib.md5(entry.url.encode()).hexdigest()
        filepath = settings.ARCHIVE_PATH / f'{filename}.json.gz'
        with gzip.open(filepath, 'wb') as f:
            f.write(article)

        entry.archive = filename

    saved = await feed_entries_db.update_archived(entry)
    if not saved:
        log.warning('Could not save archive entry %s', entry.url)


async def setup_all_dbs():
    await feed_entries_db._setup_db()
    await stats_db._setup_db()
