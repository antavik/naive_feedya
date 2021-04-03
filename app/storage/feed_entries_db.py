import datetime

import settings

from dataclasses import dataclass, field
from typing import Tuple, List, Any

from .base import execute, fetch_one, fetch_all
from utils import escape_single_quote


@dataclass
class FeedEntry:
    feed: str
    title: str
    url: str
    summary: str
    published_timestamp: float
    valid: bool
    classified: bool = field(default=False)

    def __post_init__(self):
        self.valid = bool(self.valid)
        self.classified = bool(self.classified)

    @property
    def published_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.published_timestamp)


DB_FILEPATH = settings.FEED_ENTRIES_DB_FILEPATH
FEED_ENTRIES_TABLE = 'feed_entries'


async def get(url: str) -> Tuple[Any, ...]:
    command = f"""
        SELECT * FROM {FEED_ENTRIES_TABLE}
        WHERE url = '{url}'
    """

    result = await fetch_one(DB_FILEPATH, command)

    return FeedEntry(*result)


async def fetch_all_entries() -> List[Tuple[Any, ...]]:
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
        SELECT * FROM {FEED_ENTRIES_TABLE}
        WHERE url = '{url}'
    """

    result = await fetch_one(DB_FILEPATH, command)

    return result is not None


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
        hours_delta: int
        ) -> Tuple[FeedEntry, ...]:
    command = f"""
        SELECT * FROM {FEED_ENTRIES_TABLE}
        WHERE
            valid = {int(valid)} AND
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


async def is_classified(url: str) -> int:
    command = f"""
        SELECT classified
        FROM {FEED_ENTRIES_TABLE}
        WHERE url = '{url}'
    """

    result = await fetch_one(DB_FILEPATH, command)

    return result[0] if result else None


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


def feed_entry_tuple_factory(feed_entry_list: List) -> Tuple[Any, ...]:
    return (
        feed_entry_list[0],
        feed_entry_list[1],
        feed_entry_list[2],
        feed_entry_list[3],
        feed_entry_list[4],
        int(feed_entry_list[5]),
        int(feed_entry_list[6]),
    )
