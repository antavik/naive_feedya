import settings

from typing import Tuple, Optional
from collections.abc import Iterable

from .base import execute, fetch_one, fetch_all, execute_many
from .entities import FeedEntry, feed_entry_as_tuple
from utils import escape_single_quote

DB_FILEPATH = settings.FEED_ENTRIES_DB_FILEPATH
FEED_ENTRIES_TABLE = 'feed_entries'


async def get(url: str) -> FeedEntry:
    command = f"""
        SELECT *
        FROM {FEED_ENTRIES_TABLE}
        WHERE url = '{url}'
    """

    result = await fetch_one(DB_FILEPATH, command)

    return FeedEntry(*result)


async def fetch_all_entries() -> Tuple[FeedEntry, ...]:
    command = f"""
        SELECT * FROM {FEED_ENTRIES_TABLE}
    """

    result = await fetch_all(DB_FILEPATH, command)

    return tuple(FeedEntry(*r) for r in result)


async def save(feed_entry: FeedEntry) -> int:
    command = f"""
        INSERT OR IGNORE INTO {FEED_ENTRIES_TABLE}
        (feed, title, url, summary, published_date, valid, classified)
        VALUES(
            '{feed_entry.feed}',
            '{escape_single_quote(feed_entry.title)}',
            '{feed_entry.url}',
            '{escape_single_quote(feed_entry.summary)}',
            {feed_entry.published_timestamp},
            {int(feed_entry.valid)},
            {int(feed_entry.classified)}
        )
    """

    result = await execute(DB_FILEPATH, command)

    return result.rowcount


async def exists(url: str) -> bool:
    command = f"""
        SELECT url
        FROM {FEED_ENTRIES_TABLE}
        WHERE url = '{url}'
    """

    result = await fetch_one(DB_FILEPATH, command)

    return result is not None


async def filter_exist_urls(urls: Iterable[str]) -> Tuple[str, ...]:
    quoted_urls = (f"'{escape_single_quote(url)}'" for url in urls)

    command = f"""
        SELECT url
        FROM {FEED_ENTRIES_TABLE}
        WHERE url IN ({', '.join(quoted_urls)})
    """

    result = await fetch_all(DB_FILEPATH, command)

    return tuple(url[0] for url in result)


async def remove_old(
        days_delta: int = settings.FEED_ENTRIES_DAYS_THRESHOLD
        ) -> int:
    command = f"""
        DELETE FROM {FEED_ENTRIES_TABLE}
        WHERE
            published_date <
            CAST(strftime('%s', date('now', '-{days_delta} days')) as integer)
    """

    result = await execute(DB_FILEPATH, command)

    return result.rowcount


async def fetch_last_entries(
        valid: bool,
        hours_delta: int,
        feeds: Iterable[str]
        ) -> Tuple[FeedEntry, ...]:
    quoted_titles = (f"'{f}'" for f in feeds)

    command = f"""
        SELECT *
        FROM {FEED_ENTRIES_TABLE}
        WHERE
            valid = {int(valid)} AND
            feed IN ({", ".join(quoted_titles)}) AND
            published_date >
            CAST(
                strftime('%s', date('now', '-{hours_delta} hours')) as integer
            )
        ORDER BY published_date DESC
    """

    news = await fetch_all(DB_FILEPATH, command)

    return tuple(FeedEntry(*n) for n in news)


async def update_validity(url: str, label: bool) -> int:
    command = f"""
        UPDATE {FEED_ENTRIES_TABLE}
        SET valid = {int(label)}, classified = 1
        WHERE url = '{url}'
    """

    result = await execute(DB_FILEPATH, command)

    return result.rowcount


async def is_classified(url: str) -> Optional[bool]:
    command = f"""
        SELECT classified
        FROM {FEED_ENTRIES_TABLE}
        WHERE url = '{url}'
    """

    result = await fetch_one(DB_FILEPATH, command)

    return result if result is None else bool(result[0])


async def save_many(feeds: Iterable[FeedEntry]) -> int:
    command = f"""
        INSERT OR IGNORE INTO {FEED_ENTRIES_TABLE}
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    seq_feed_entries_data = (
        feed_entry_as_tuple(f)
        for f in feeds
    )

    result = await execute_many(
        DB_FILEPATH,
        command,
        seq_feed_entries_data
    )

    return result.rowcount


async def _setup_db():
    command = f"""
        CREATE TABLE IF NOT EXISTS {FEED_ENTRIES_TABLE}(
            feed TEXT,
            title TEXT,
            url TEXT PRIMARY KEY,
            summary BLOB,
            published_date DATETIME,
            valid BOOLEAN,
            classified BOOLEAN DEFAULT 0
        )
    """

    await execute(DB_FILEPATH, command)
    print('Feed entries DB created')
