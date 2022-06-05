import typing as t

import aiosqlite
from aiosqlite import Cursor, Row

from pathlib import Path


async def execute(db_filepath: Path, command: str, *params) -> Cursor:
    async with aiosqlite.connect(db_filepath) as db:
        result = await db.execute(command, params)

        await db.commit()

    return result


async def execute_many(db_filepath: Path, command: str, *params) -> Cursor:
    async with aiosqlite.connect(db_filepath) as db:
        result = await db.executemany(command, params)

        await db.commit()

    return result


async def fetch_one(
        db_filepath: Path,
        command: str,
        *params
) -> t.Optional[Row]:
    async with aiosqlite.connect(db_filepath) as db:
        async with db.execute(command, params) as cursor:
            result = await cursor.fetchone()

    return result


async def fetch_all(
        db_filepath: Path,
        command: str,
        *params
) -> t.Iterable[Row]:
    async with aiosqlite.connect(db_filepath) as db:
        result = await db.execute_fetchall(command, params)

    return result
