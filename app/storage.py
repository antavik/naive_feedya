import datetime

import aiosqlite
from aiosqlite.cursor import Cursor

import settings

from math import log
from typing import TypeVar, Tuple, Iterable, List, Any
from dataclasses import dataclass, field

_Number = TypeVar('_Number', int, float)


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


@dataclass
class TokenStats:
    token: str
    news: int
    spam: int

    def __hash__(self) -> int:
        return hash(self.token)


@dataclass
class DocCounter:
    language: str
    news: int
    spam: int


class BaseStorage:

    _db_filepath = None

    @classmethod
    async def _execute(cls, command: str) -> Cursor:
        async with aiosqlite.connect(cls._db_filepath) as db:
            result = await db.execute(command)

            await db.commit()

        return result

    @classmethod
    async def _execute_many(cls, command: str, iterable: Iterable) -> Cursor:
        async with aiosqlite.connect(cls._db_filepath) as db:
            result = await db.executemany(command, iterable)

            await db.commit()

        return result

    @classmethod
    async def _fetch_one(cls, command: str) -> Tuple[Any, ...]:
        async with aiosqlite.connect(cls._db_filepath) as db:
            async with db.execute(command) as cursor:
                result = await cursor.fetchone()

        return result

    @classmethod
    async def _fetch_all(cls, command: str) -> List[Tuple[Any, ...]]:
        async with aiosqlite.connect(cls._db_filepath) as db:
            async with db.execute(command) as cursor:
                result = await cursor.fetchall()

        return result


class FeedEntriesStorage(BaseStorage):

    _db_filepath = settings.FEED_ENTRIES_DB_FILEPATH

    FEED_ENTRIES_TABLE = 'feed_entries'

    @classmethod
    async def get(cls, url: str) -> Tuple[Any, ...]:
        command = f"""
            SELECT * FROM {cls.FEED_ENTRIES_TABLE}
            WHERE url = '{url}'
        """

        result = await cls._fetch_one(command)

        return FeedEntry(*result)

    @classmethod
    async def fetch_all(cls) -> List[Tuple[Any, ...]]:
        command = f"""
            SELECT * FROM {cls.FEED_ENTRIES_TABLE}
        """

        result = await cls._fetch_all(command)

        return tuple(FeedEntry(*r) for r in result)

    @classmethod
    async def save(cls, feed_entry: FeedEntry) -> int:
        command = f"""
            INSERT OR IGNORE INTO {cls.FEED_ENTRIES_TABLE}
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

        result = await cls._execute(command)

        return result.rowcount

    @classmethod
    async def exists(cls, url: str) -> bool:
        command = f"""
            SELECT * FROM {cls.FEED_ENTRIES_TABLE}
            WHERE url = '{url}'
        """

        result = await cls._fetch_one(command)

        return result is not None

    @classmethod
    async def remove_old(
            cls,
            days_delta: int=settings.FEED_ENTRIES_DAYS_THRESHOLD
        ) -> int:
        command = f"""
            DELETE FROM {cls.FEED_ENTRIES_TABLE}
            WHERE
                published_date <
                CAST(strftime('%s', date('now', '-{days_delta} days')) as integer)
        """

        result = await cls._execute(command)

        return result.rowcount

    @classmethod
    async def fetch_last_entries(
            cls,
            valid: bool,
            hours_delta: int
        ) -> Tuple[FeedEntry, ...]:
        command = f"""
            SELECT * FROM {cls.FEED_ENTRIES_TABLE}
            WHERE 
                valid = {int(valid)} AND
                published_date >
                CAST(strftime('%s', date('now', '-{hours_delta} hours')) as integer)
            ORDER BY published_date DESC
        """

        news = await cls._fetch_all(command)

        return tuple(FeedEntry(*n) for n in news)

    @classmethod
    async def update_validity(cls, url: str, label: bool) -> int:
        command = f"""
            UPDATE {cls.FEED_ENTRIES_TABLE}
            SET valid = {int(label)}, classified = 1
            WHERE url = '{url}'
        """

        result = await cls._execute(command)

        return result.rowcount

    @classmethod
    async def is_classified(cls, url: str) -> int:
        command = f"""
            SELECT classified
            FROM {cls.FEED_ENTRIES_TABLE}
            WHERE url = '{url}'
        """

        result = await cls._fetch_one(command)

        return result[0] if result else None

    @classmethod
    async def _setup_db(cls):
        command = f"""
            CREATE TABLE IF NOT EXISTS {cls.FEED_ENTRIES_TABLE}(
                feed TEXT,
                title TEXT,
                url TEXT PRIMARY KEY,
                summary BLOB,
                published_date DATETIME,
                valid BOOLEAN,
                classified BOOLEAN DEFAULT 0
            )
        """

        await cls._execute(command)


class StatsStorage(BaseStorage):

    _db_filepath = settings.STATS_DB_FILEPATH

    ENG_STATS_TABLE = f'{settings.ENGLISH_LANGUAGE}_token_stats'
    DOC_STATS_TABLE = 'doc_stats'

    @classmethod
    async def get_token_stats(cls, token: str) -> Tuple[Any, ...]:
        command = f"""
            SELECT * FROM {cls.ENG_STATS_TABLE}
            WHERE token = '{token}'
        """

        result = await cls._fetch_one(command)

        return TokenStats(*result)

    @classmethod
    async def get_doc_counter(cls, language: str) -> Tuple[Any, ...]:
        command = f"""
            SELECT * FROM {cls.DOC_STATS_TABLE}
            WHERE language = '{language}'
        """

        result = await cls._fetch_one(command)

        return DocCounter(*result)

    @classmethod
    async def save_or_increment_news_token(cls, token: str) -> int:
        command = f'''
            INSERT INTO {cls.ENG_STATS_TABLE}(token, news, spam)
            VALUES("{token}", 1, 0)
            ON CONFLICT(token)
            DO UPDATE SET news = news + 1
        '''

        result = await cls._execute(command)

        return result.rowcount

    @classmethod
    async def save_or_increment_spam_token(cls, token: str) -> int:
        command = f'''
            INSERT INTO {cls.ENG_STATS_TABLE}(token, news, spam)
            VALUES("{token}", 0, 1) 
            ON CONFLICT(token) 
            DO UPDATE SET spam = spam + 1
        '''

        result = await cls._execute(command)

        return result.rowcount

    @classmethod
    async def increment_doc_counter(
            cls,
            language: str,
            counter_type: str
        ) -> int:
        command = f"""
            UPDATE {cls.DOC_STATS_TABLE}
            SET {counter_type} = {counter_type} + 1
            WHERE language = '{language}'
        """

        result = await cls._execute(command)

        return result.rowcount

    @classmethod
    async def get_docs_p_values(cls, language: str) -> int:
        command = f"""
            SELECT log(1.0 * news / (news + spam)), log(1.0 * spam / (news + spam))
            FROM {cls.DOC_STATS_TABLE}
            WHERE language = '{language}'
        """

        async with aiosqlite.connect(cls._db_filepath) as db:
            await db.create_function('log', 1, log, deterministic=True)

            async with db.execute(command) as cursor:
                docs_p_news, docs_p_spam = await cursor.fetchone()

        return docs_p_news, docs_p_spam

    @classmethod
    async def get_token_p_values(cls, token: str) -> Tuple[_Number, _Number]:
        command = f"""
            SELECT *
            FROM (
                SELECT log((1.0 + T2.docs_counter) / T1.tokens_sum)
                FROM
                (
                    SELECT sum(c) as tokens_sum
                    FROM (
                        SELECT count(*) AS c FROM {cls.ENG_STATS_TABLE} WHERE news > 0
                        UNION ALL
                        SELECT count(*) AS c FROM {cls.ENG_STATS_TABLE}
                    )
                ) T1
                JOIN
                ( 
                    SELECT CASE WHEN count(*) > 0
                    THEN news ELSE 0 END AS docs_counter
                    FROM {cls.ENG_STATS_TABLE} WHERE token = "{token}"
                ) T2

                UNION ALL

                SELECT log((1.0 + T2.docs_counter) / T1.tokens_sum)
                FROM 
                (
                    SELECT sum(c) as tokens_sum
                    FROM (
                        SELECT count(*) AS c FROM {cls.ENG_STATS_TABLE} WHERE spam > 0 
                        UNION ALL
                        SELECT count(*) AS c FROM {cls.ENG_STATS_TABLE}
                    )
                ) T1
                JOIN
                ( 
                    SELECT CASE WHEN count(*) > 0
                    THEN spam ELSE 0 END AS docs_counter
                    FROM {cls.ENG_STATS_TABLE} WHERE token = "{token}"
                ) T2
            )
        """

        async with aiosqlite.connect(cls._db_filepath) as db:
            await db.create_function('log', 1, log, deterministic=True)

            async with db.execute(command) as cursor:
                result = await cursor.fetchall()

        token_p_news, token_p_spam = (r[0] for r in result)
        
        return token_p_news, token_p_spam

    @classmethod
    async def reverse_token_stats(
            cls,
            token: str,
            new_label: str,
            old_label: str
        ):
        command = f"""
            UPDATE {cls.ENG_STATS_TABLE}
            SET {new_label} = {new_label} + 1, {old_label} = {old_label} - 1
            WHERE token = '{token}'
        """

        result = await cls._execute(command)

        return result.rowcount

    @classmethod
    async def _setup_db(cls):
        create_table_command = f"""
            CREATE TABLE IF NOT EXISTS {cls.ENG_STATS_TABLE}(
                token TEXT PRIMARY KEY,
                news INTEGER DEFAULT 0,
                spam INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS {cls.DOC_STATS_TABLE}(
                language TEXT PRIMARY KEY,
                news INTEGER DEFAULT 0,
                spam INTEGER DEFAULT 0
            )
        """

        insert_requred_values_command = f"""
            INSERT OR IGNORE INTO {stats_db.DOC_STATS_TABLE}
            (language)
            VALUES(?)
        """

        async with aiosqlite.connect(cls._db_filepath) as db:
            await db.executescript(create_table_command)

            await db.executemany(
                insert_requred_values_command,
                ((l,) for l in settings.SUPPORTED_LANGUAGES)
            )

            await db.commit()


feed_entries_db = FeedEntriesStorage
stats_db = StatsStorage


def escape_single_quote(string: str) -> str:
    return string.replace('\'', '\'\'')


def feed_entry_to_tuple(feed_entry_list: FeedEntry) -> Tuple[Any, ...]:
    return (
        feed_entry_list[0],
        feed_entry_list[1],
        feed_entry_list[2],
        feed_entry_list[3],
        feed_entry_list[4],
        int(feed_entry_list[5]),
        int(feed_entry_list[6]),
    )


if __name__ == '__main__':
    import asyncio


    async def setup_dbs():
        await feed_entries_db._setup_db()
        await stats_db._setup_db()


    print('Setup new DBs')

    asyncio.run(setup_dbs())

    print('DBs have been setuped')
