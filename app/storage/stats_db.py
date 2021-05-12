import math

import aiosqlite

import settings

from typing import TypeVar, Tuple, Optional

from .base import execute, fetch_one
from .entities import TokenStats, DocCounter

_Number = TypeVar('_Number', int, float)

DB_FILEPATH = settings.STATS_DB_FILEPATH
ENG_STATS_TABLE = f'{settings.ENGLISH_LANGUAGE}_token_stats'
DOC_STATS_TABLE = 'doc_stats'


async def get_token_stats(token: str) -> TokenStats:
    command = f"""
        SELECT * FROM {ENG_STATS_TABLE}
        WHERE token = '{token}'
    """

    result = await fetch_one(DB_FILEPATH, command)

    return TokenStats(*result)


async def get_doc_counter(language: str) -> DocCounter:
    command = f"""
        SELECT * FROM {DOC_STATS_TABLE}
        WHERE language = '{language}'
    """

    result = await fetch_one(DB_FILEPATH, command)

    return DocCounter(*result)


async def save_or_increment_news_token(token: str) -> int:
    command = f"""
        INSERT INTO {ENG_STATS_TABLE}(token, news, spam)
        VALUES("{token}", 1, 0)
        ON CONFLICT(token)
        DO UPDATE SET news = news + 1
    """

    result = await execute(DB_FILEPATH, command)

    return result.rowcount


async def save_or_increment_spam_token(token: str) -> int:
    command = f"""
        INSERT INTO {ENG_STATS_TABLE}(token, news, spam)
        VALUES("{token}", 0, 1)
        ON CONFLICT(token)
        DO UPDATE SET spam = spam + 1
    """

    result = await execute(DB_FILEPATH, command)

    return result.rowcount


async def increment_doc_counter(
        language: str,
        counter_type: str
        ) -> int:
    command = f"""
        UPDATE {DOC_STATS_TABLE}
        SET {counter_type} = {counter_type} + 1
        WHERE language = '{language}'
    """

    result = await execute(DB_FILEPATH, command)

    return result.rowcount


async def get_docs_p_values(
        language: str) -> Tuple[Optional[_Number], Optional[_Number]]:
    command = f"""
        SELECT news_p, spam_p
        FROM
        (
            SELECT CASE
            WHEN news > 0
            THEN log(1.0 * news / (news + spam))
            ELSE NULL
            END AS news_p
            FROM {DOC_STATS_TABLE}
            WHERE language = '{language}'
        ) NEWS_STATS
        JOIN
        (
            SELECT CASE
            WHEN spam > 0
            THEN log(1.0 * spam / (news + spam))
            ELSE NULL
            END AS spam_p
            FROM {DOC_STATS_TABLE}
            WHERE language = '{language}'
        ) SPAM_STATS
    """

    async with aiosqlite.connect(DB_FILEPATH) as db:
        await db.create_function('log', 1, math.log, deterministic=True)

        async with db.execute(command) as cursor:
            docs_p_news, docs_p_spam = await cursor.fetchone()

    return docs_p_news, docs_p_spam


async def get_token_p_values(token: str) -> Tuple[_Number, _Number]:
    command = f"""
        SELECT *
        FROM (
            SELECT log((1.0 + T1.token_frequency) / T2.tokens_sum)
            FROM
            (
                SELECT CASE WHEN count(*) > 0
                THEN news ELSE 0 END AS token_frequency
                FROM {ENG_STATS_TABLE} WHERE token = '{token}'
            ) T1
            JOIN
            (
                SELECT sum(c) as tokens_sum
                FROM (
                    SELECT count(*) AS c FROM {ENG_STATS_TABLE} WHERE news > 0
                    UNION ALL
                    SELECT count(*) AS c FROM {ENG_STATS_TABLE}
                )
            ) T2

            UNION ALL

            SELECT log((1.0 + T1.token_frequency) / T2.tokens_sum)
            FROM
            (
                SELECT CASE WHEN count(*) > 0
                THEN spam ELSE 0 END AS token_frequency
                FROM {ENG_STATS_TABLE} WHERE token = '{token}'
            ) T1
            JOIN
            (
                SELECT sum(c) as tokens_sum
                FROM (
                    SELECT count(*) AS c FROM {ENG_STATS_TABLE} WHERE spam > 0
                    UNION ALL
                    SELECT count(*) AS c FROM {ENG_STATS_TABLE}
                )
            ) T2
        )
    """

    async with aiosqlite.connect(DB_FILEPATH) as db:
        await db.create_function('log', 1, math.log, deterministic=True)

        async with db.execute(command) as cursor:
            result = await cursor.fetchall()

    token_p_news, token_p_spam = (r[0] for r in result)

    return token_p_news, token_p_spam


async def reverse_token_stats(
        token: str,
        new_label: str,
        old_label: str
        ) -> int:
    command = f"""
        UPDATE {ENG_STATS_TABLE}
        SET {new_label} = {new_label} + 1, {old_label} = {old_label} - 1
        WHERE token = '{token}'
    """

    result = await execute(DB_FILEPATH, command)

    return result.rowcount


async def _setup_db():
    create_table_command = f"""
        CREATE TABLE IF NOT EXISTS {ENG_STATS_TABLE}(
            token TEXT PRIMARY KEY,
            news INTEGER DEFAULT 0,
            spam INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS {DOC_STATS_TABLE}(
            language TEXT PRIMARY KEY,
            news INTEGER DEFAULT 0,
            spam INTEGER DEFAULT 0
        )
    """

    insert_requred_values_command = f"""
        INSERT OR IGNORE INTO {DOC_STATS_TABLE}
        (language)
        VALUES(?)
    """

    async with aiosqlite.connect(DB_FILEPATH) as db:
        await db.executescript(create_table_command)

        await db.executemany(
            insert_requred_values_command,
            ((lang,) for lang in settings.SUPPORTED_LANGUAGES)
        )

        await db.commit()
    
    print('Stats DB created')
