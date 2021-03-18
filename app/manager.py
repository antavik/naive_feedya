import time
import logging

from feeds import Feed, FEEDS_REGISTRY, FEEDS
from storage import FeedEntry, feed_entries_db 
from feed_classifier.classifier import classify, update_stats
from feed_classifier.parser import parse
from web.rendering import render_html_page


async def process_feed(feed: Feed) -> None:
    parsed_feed = await parse(feed)

    if not parsed_feed:
        return

    for entry in parsed_feed.entries:
        if not await feed_entries_db.exists(entry.link):
            published_timestamp = time.mktime(
                entry.get('published_parsed') or entry.get('updated_parsed')
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
                    summary=published_summary,
                    valid=valid,
                )
            )
    else:
        logging.info('%s feed entries saved in DB', feed.title)


async def clean_feed_entries_db():
    removed = await feed_entries_db.remove_old()

    if removed:
        logging.info('Feed entries DB cleaned. Removed %d entries', removed)


async def get_news_page() -> str:
    feed_to_entries = {f: [] for f in FEEDS}

    news_entries = await feed_entries_db.fetch_last_news()

    for entry in news_entries:
        feed = FEEDS_REGISTRY[entry.feed]
        feed_to_entries[feed].append(entry)

    html_page = render_html_page(feed_to_entries, 'news')

    return html_page


async def get_spam_page() -> str:
    feed_to_entries = {f: [] for f in FEEDS}

    spam_entries = await feed_entries_db.fetch_last_spam()

    for entry in spam_entries:
        feed = FEEDS_REGISTRY[entry.feed]
        feed_to_entries[feed].append(entry)

    html_page = render_html_page(feed_to_entries, 'spam')

    return html_page


async def update_feed_classifier(feedback):
    await update_stats(
        document=feedback.entry_title,
        label=feedback.entry_is_valid,
        language=feedback.entry_language,
    )

    await feed_entries_db.update_validity(
        url=feedback.entry_url,
        label=feedback.entry_is_valid,
    )
