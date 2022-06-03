import math

import aiosqlite

import settings
import constants as const

from typing import TypeVar, Optional, Union

from .base import execute, fetch_one
from .entities import TokenStats, DocCounter

_Number = TypeVar('_Number', int, float)

DB_FILEPATH = settings.STATS_DB_FILEPATH
TOKENS_TABLE = settings.STATS_TABLE
DOC_TABLE = 'doc_stats'


async def get_token_stats(token: str) -> Union[None, TokenStats]:
    query = f"""
        SELECT * FROM {TOKENS_TABLE}
        WHERE token = ?
    """

    result = await fetch_one(DB_FILEPATH, query, token)

    return result and TokenStats(*result)


async def get_doc_counter(language: const.Language) -> Union[None, DocCounter]:
    query = f"""
        SELECT * FROM {DOC_TABLE}
        WHERE language = ?
    """

    result = await fetch_one(DB_FILEPATH, query, language.value)
    if result:
        _, news, spam = result

        return DocCounter(language, news, spam)

    return result


async def save_or_increment_news_token(token: str) -> int:
    query = f"""
        INSERT INTO {TOKENS_TABLE}(token, news, spam)
        VALUES(?, 1, 0)
        ON CONFLICT(token)
        DO UPDATE SET news = news + 1
    """

    result = await execute(DB_FILEPATH, query, token)

    return result.rowcount


async def save_or_increment_spam_token(token: str) -> int:
    query = f"""
        INSERT INTO {TOKENS_TABLE}(token, news, spam)
        VALUES(?, 0, 1)
        ON CONFLICT(token)
        DO UPDATE SET spam = spam + 1
    """

    result = await execute(DB_FILEPATH, query, token)

    return result.rowcount


async def increment_doc_counter(
        language: const.Language,
        counter_type: str
) -> int:
    query = f"""
        UPDATE {DOC_TABLE}
        SET {counter_type} = {counter_type} + 1
        WHERE language = ?
    """

    result = await execute(DB_FILEPATH, query, language.value)

    return result.rowcount


async def get_docs_p_values(
        language: const.Language
) -> tuple[Optional[_Number], Optional[_Number]]:
    query = f"""
        SELECT news_p, spam_p
        FROM
        (
            SELECT CASE
            WHEN news > 0
            THEN log(1.0 * news / (news + spam))
            ELSE NULL
            END AS news_p
            FROM {DOC_TABLE}
            WHERE language = ?
        ) NEWS_STATS
        JOIN
        (
            SELECT CASE
            WHEN spam > 0
            THEN log(1.0 * spam / (news + spam))
            ELSE NULL
            END AS spam_p
            FROM {DOC_TABLE}
            WHERE language = ?
        ) SPAM_STATS
    """

    async with aiosqlite.connect(DB_FILEPATH) as db:
        await db.create_function('log', 1, math.log, deterministic=True)

        async with db.execute(query, (language.value, language.value)) as cursor:  # noqa
            docs_p_news, docs_p_spam = await cursor.fetchone()

    return docs_p_news, docs_p_spam


async def get_token_p_values(token: str) -> tuple[_Number, _Number]:
    command = f"""
        SELECT *
        FROM (
            SELECT log((1.0 + T1.token_frequency) / T2.tokens_sum)
            FROM
            (
                SELECT CASE WHEN count(*) > 0
                THEN news ELSE 0 END AS token_frequency
                FROM {TOKENS_TABLE} WHERE token = ?
            ) T1
            JOIN
            (
                SELECT sum(c) as tokens_sum
                FROM (
                    SELECT count(*) AS c FROM {TOKENS_TABLE} WHERE news > 0
                    UNION ALL
                    SELECT count(*) AS c FROM {TOKENS_TABLE}
                )
            ) T2

            UNION ALL

            SELECT log((1.0 + T1.token_frequency) / T2.tokens_sum)
            FROM
            (
                SELECT CASE WHEN count(*) > 0
                THEN spam ELSE 0 END AS token_frequency
                FROM {TOKENS_TABLE} WHERE token = ?
            ) T1
            JOIN
            (
                SELECT sum(c) as tokens_sum
                FROM (
                    SELECT count(*) AS c FROM {TOKENS_TABLE} WHERE spam > 0
                    UNION ALL
                    SELECT count(*) AS c FROM {TOKENS_TABLE}
                )
            ) T2
        )
    """  # noqa

    async with aiosqlite.connect(DB_FILEPATH) as db:
        await db.create_function('log', 1, math.log, deterministic=True)

        async with db.execute(command, (token, token)) as cursor:
            result = await cursor.fetchall()

    token_p_news, token_p_spam = (r[0] for r in result)

    return token_p_news, token_p_spam


async def get_tokens_p_values(tokens: list[str]) -> tuple[_Number, _Number]:
    query = f"""
        WITH
        doc(token) AS (
            VALUES {','.join('(?)' for _ in range(len(tokens)))}
        ),
        join_t AS (
            SELECT 
                doc.token AS token,
                CASE WHEN {TOKENS_TABLE}.news IS NULL THEN 0 ELSE {TOKENS_TABLE}.news END AS news,
                CASE WHEN {TOKENS_TABLE}.spam IS NULL THEN 0 ELSE {TOKENS_TABLE}.spam END AS spam
            FROM (
                SELECT token FROM doc UNION
                SELECT token FROM {TOKENS_TABLE}
            )
            LEFT JOIN doc USING (token)
            LEFT JOIN {TOKENS_TABLE} USING (token)
            WHERE doc.token IS NOT NULL
        ),
        news_sum_t AS (
            SELECT sum(c) AS s
            FROM (
                SELECT count(*) AS c FROM {TOKENS_TABLE} WHERE news > 0 UNION ALL
                SELECT count(*) AS c FROM {TOKENS_TABLE}
            )
        ),
        spam_sum_t AS (
            SELECT sum(c) AS s
            FROM (
                SELECT count(*) AS c FROM {TOKENS_TABLE} WHERE spam > 0 UNION ALL
                SELECT count(*) AS c FROM {TOKENS_TABLE}
            )
        )
        SELECT sum(news_p), sum(spam_p)
        FROM (
            SELECT 
                join_t.token                            AS token,
                log((1.0 + join_t.news) / news_sum_t.s) AS news_p,
                log((1.0 + join_t.spam) / spam_sum_t.s) AS spam_p
            FROM join_t
            JOIN news_sum_t
            JOIN spam_sum_t
        )
    """  # noqa

    print(query)

    async with aiosqlite.connect(DB_FILEPATH) as db:
        await db.create_function('log', 1, math.log, deterministic=True)

        async with db.execute(query, tokens) as cursor:
            tokens_p_news, tokens_p_spam = await cursor.fetchone()

    return tokens_p_news, tokens_p_spam


async def reverse_token_stats(
        token: str,
        new_label: str,
        old_label: str
) -> int:
    query = f"""
        UPDATE {TOKENS_TABLE}
        SET {new_label} = {new_label} + 1, {old_label} = {old_label} - 1
        WHERE token = ?
    """

    result = await execute(DB_FILEPATH, query, token)

    return result.rowcount


async def reverse_docs_stats(
        new_label: str,
        old_label: str,
        language: const.Language
) -> int:
    query = f"""
        UPDATE {DOC_TABLE}
        SET {new_label} = {new_label} + 1, {old_label} = {old_label} - 1
        WHERE language = ?
    """

    result = await execute(
        DB_FILEPATH, query, language.value
    )

    return result.rowcount


async def _setup_db():
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TOKENS_TABLE}(
            token TEXT PRIMARY KEY,
            news INTEGER DEFAULT 0,
            spam INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS {DOC_TABLE}(
            language TEXT PRIMARY KEY,
            news INTEGER DEFAULT 0,
            spam INTEGER DEFAULT 0
        );
    """

    insert_required_values_query = f"""
        INSERT OR IGNORE INTO {DOC_TABLE}
        (language)
        VALUES(?)
    """

    async with aiosqlite.connect(DB_FILEPATH) as db:
        await db.executescript(create_table_query)

        await db.execute(
            insert_required_values_query, (settings.APP_LANG.value,)
        )

        await db.commit()
