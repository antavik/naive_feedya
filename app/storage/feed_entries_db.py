import settings

from typing import Tuple, Optional
from collections.abc import Iterable

from .base import execute, fetch_one, fetch_all, execute_many
from .entities import FeedEntry, feed_entry_as_tuple
from utils import escape_single_quote

DB_FILEPATH = settings.FEED_ENTRIES_DB_FILEPATH
FEED_ENTRIES_TABLE = 'feed_entries'


async def get(url: str) -> FeedEntry:
    query = f"""
        SELECT *
        FROM {FEED_ENTRIES_TABLE}
        WHERE url = ?
    """

    result = await fetch_one(DB_FILEPATH, query, url)

    return FeedEntry(*result)


async def fetch_all_entries() -> Tuple[FeedEntry, ...]:
    query = f"""
        SELECT * FROM {FEED_ENTRIES_TABLE}
    """

    result = await fetch_all(DB_FILEPATH, query)

    return tuple(FeedEntry(*r) for r in result)


async def save(feed_entry: FeedEntry) -> int:
    query = f"""
        INSERT OR IGNORE INTO {FEED_ENTRIES_TABLE}
        (feed, title, url, summary, published, parsed, valid, classified, archive)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
    """  # noqa

    result = await execute(
        DB_FILEPATH, query, *feed_entry_as_tuple(feed_entry)
    )

    return result.rowcount


async def exists(url: str) -> bool:
    query = f"""
        SELECT url
        FROM {FEED_ENTRIES_TABLE}
        WHERE url = ?
    """

    result = await fetch_one(DB_FILEPATH, query, url)

    return result is not None


async def filter_exist_urls(urls: Iterable[str]) -> set[str]:
    quoted_urls = (f"'{escape_single_quote(url)}'" for url in urls)

    query = f"""
        SELECT url
        FROM {FEED_ENTRIES_TABLE}
        WHERE url IN ({', '.join(quoted_urls)})
    """

    result = await fetch_all(DB_FILEPATH, query)

    return {url[0] for url in result}


async def remove_old(
        days_delta: int = settings.FEED_ENTRIES_DAYS_THRESHOLD
) -> int:
    query = f"""
        DELETE FROM {FEED_ENTRIES_TABLE}
        WHERE
            parsed < CAST(
                strftime('%s', date('now', '-{days_delta} days')) as integer
            ) AND
            classified = 0 OR (classified = 1 AND valid = 0)
    """

    result = await execute(DB_FILEPATH, query)

    return result.rowcount


async def fetch_last_entries(
        valid: bool,
        hours_delta: int,
        feeds: Iterable[str]
) -> Tuple[FeedEntry, ...]:
    quoted_titles = (f"'{f}'" for f in feeds)

    query = f"""
        SELECT *
        FROM {FEED_ENTRIES_TABLE}
        WHERE
            valid = {int(valid)} AND
            feed IN ({", ".join(quoted_titles)}) AND
            parsed >
            CAST(
                strftime('%s', date('now', '-{hours_delta} hours')) as integer
            )
        ORDER BY parsed DESC
    """

    result = await fetch_all(DB_FILEPATH, query)

    return tuple(FeedEntry(*r) for r in result)


async def update_validity(url: str, label: bool) -> int:
    query = f"""
        UPDATE {FEED_ENTRIES_TABLE}
        SET valid = ?, classified = 1
        WHERE url = ?
    """

    result = await execute(DB_FILEPATH, query, label, url)

    return result.rowcount


async def is_classified(url: str) -> Optional[bool]:
    query = f"""
        SELECT classified
        FROM {FEED_ENTRIES_TABLE}
        WHERE url = ?
    """

    result = await fetch_one(DB_FILEPATH, query, url)

    return result if result is None else bool(result[0])


async def save_many(feeds: Iterable[FeedEntry]) -> int:
    query = f"""
        INSERT OR IGNORE INTO {FEED_ENTRIES_TABLE}
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    seq_feed_entries_data = (feed_entry_as_tuple(f) for f in feeds)

    result = await execute_many(
        DB_FILEPATH, query, *seq_feed_entries_data
    )

    return result.rowcount


async def fetch_unarchived_valid_classified_entries() -> Tuple[FeedEntry, ...]:
    query = f"""
        SELECT *
        FROM {FEED_ENTRIES_TABLE}
        WHERE valid = 1 AND classified = 1 AND archive IS NULL
    """

    result = await fetch_all(DB_FILEPATH, query)

    return tuple(FeedEntry(*r) for r in result)


async def update_archived(feed_entry: FeedEntry) -> int:
    query = f"""
        UPDATE {FEED_ENTRIES_TABLE}
        SET archive = ?
        WHERE url = ?
    """

    result = await execute(
        DB_FILEPATH, query, feed_entry.archive, feed_entry.url
    )

    return result.rowcount


async def _setup_db():
    query = f"""
        CREATE TABLE IF NOT EXISTS {FEED_ENTRIES_TABLE}(
            feed TEXT,
            title TEXT,
            url TEXT PRIMARY KEY,
            summary BLOB,
            published DATETIME,
            parsed DATETIME,
            valid BOOLEAN,
            classified BOOLEAN DEFAULT 0,
            archive TEXT DEFAULT NULL
        )
    """

    await execute(DB_FILEPATH, query)
