import datetime
import tempfile

import pytest

import settings

from pathlib import Path
from dataclasses import astuple

from faker import Faker

from constants import ENGLISH
from storage import (
    base,
    feed_entries_db,
    stats_db,
)
from storage.entities import (
    FeedEntry,
    DocCounter,
    TokenStats,
    feed_entry_as_tuple,
)

TEST_DB_FILENAME = 'temp_db.sqlite'
TEST_DB_ROWS_COUNT = 20

fake = Faker()
Faker.seed(TEST_DB_ROWS_COUNT)


@pytest.fixture
def fake_feed_entry():
    fake_entry = FeedEntry(
        feed=fake.company(),
        title='Test_title',
        url=fake.uri(),
        summary='Test_summary',
        published_timestamp=fake.unix_time(),
        valid=fake.pybool(),
    )

    return fake_entry


@pytest.fixture
def fake_news_entry(fake_feed_entry):
    fake_feed_entry.valid = True

    return fake_feed_entry


@pytest.fixture
def fake_spam_entry(fake_feed_entry):
    fake_feed_entry.valid = False

    return fake_feed_entry


@pytest.fixture
def fake_feed_entry_unclassified(fake_feed_entry):
    return fake_feed_entry


@pytest.fixture
def fake_feed_entry_classified(fake_feed_entry):
    fake_feed_entry.classified = True

    return fake_feed_entry


@pytest.fixture
def fake_seq_feed_entries():
    fake_seq = [
        FeedEntry(
            feed=fake.company(),
            title=f'Test_title-{i}',
            url=fake.uri(),
            summary=f'Test_summary-{i}',
            published_timestamp=fake.unix_time(),
            valid=fake.pybool(),
            classified=fake.pybool(),
        )
        for i in range(TEST_DB_ROWS_COUNT)
    ]

    return fake_seq


@pytest.fixture
async def fake_feed_entries_db():
    with tempfile.TemporaryDirectory() as temp_path:
        temp_db_filepath = Path(temp_path) / TEST_DB_FILENAME

        original_db_filepath = feed_entries_db.DB_FILEPATH
        feed_entries_db.DB_FILEPATH = temp_db_filepath

        await feed_entries_db._setup_db()

        yield feed_entries_db

        feed_entries_db.DB_FILEPATH = original_db_filepath


@pytest.fixture
async def fake_feed_entries_db_with_random_data(
        fake_feed_entries_db,
        fake_seq_feed_entries
        ):
    command = f"""
        INSERT INTO {fake_feed_entries_db.FEED_ENTRIES_TABLE}
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    fake_seq_feed_entries_data = (
        feed_entry_as_tuple(f)
        for f in fake_seq_feed_entries
    )

    await base.execute_many(
        fake_feed_entries_db.DB_FILEPATH,
        command,
        fake_seq_feed_entries_data
    )

    return fake_feed_entries_db


@pytest.fixture
async def fake_feed_entries_db_with_random_data_older_than_days_threshold(
        fake_feed_entries_db,
        fake_seq_feed_entries,
        datetime_now
        ):
    command = f"""
        INSERT INTO {fake_feed_entries_db.FEED_ENTRIES_TABLE}
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    test_days_threshold = settings.FEED_ENTRIES_DAYS_THRESHOLD + 1
    test_timestamp = (
        datetime_now - datetime.timedelta(days=test_days_threshold)
    ).timestamp()

    for feed_entry in fake_seq_feed_entries:
        feed_entry.published_timestamp = test_timestamp

    fake_seq_feed_entries_data = (
        feed_entry_as_tuple(f)
        for f in fake_seq_feed_entries
    )

    await base.execute_many(
        fake_feed_entries_db.DB_FILEPATH,
        command,
        fake_seq_feed_entries_data
    )

    return fake_feed_entries_db


@pytest.fixture
async def fake_feed_entries_db_with_random_data_with_recent_feed_entries(
        fake_feed_entries_db,
        fake_seq_feed_entries,
        datetime_now
        ):
    command = f"""
        INSERT INTO {fake_feed_entries_db.FEED_ENTRIES_TABLE}
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    half_row_count = TEST_DB_ROWS_COUNT // 2

    recent_feed_entries_timestamp = datetime_now.timestamp()

    for i in range(TEST_DB_ROWS_COUNT):
        if i < half_row_count:
            fake_seq_feed_entries[i].published_timestamp = recent_feed_entries_timestamp  # noqa
            fake_seq_feed_entries[i].valid = True
        else:
            fake_seq_feed_entries[i].published_timestamp = recent_feed_entries_timestamp  # noqa
            fake_seq_feed_entries[i].valid = False

    fake_seq_feed_entries_data = (
        feed_entry_as_tuple(f)
        for f in fake_seq_feed_entries
    )

    await base.execute_many(
        fake_feed_entries_db.DB_FILEPATH,
        command,
        fake_seq_feed_entries_data
    )

    return fake_feed_entries_db


@pytest.fixture
async def fake_token_stats(fake_token):
    return TokenStats(
        token=fake_token,
        news=fake.pyint(),
        spam=fake.pyint()
    )


@pytest.fixture
async def fake_seq_token_stats():
    token_stats = {
        TokenStats(
            token=fake.word(),
            news=fake.pyint(),
            spam=fake.pyint(min_value=1)
        )
        for _ in range(TEST_DB_ROWS_COUNT)
    }

    return list(token_stats)


@pytest.fixture
async def fake_eng_doc_counter():
    doc_counter = DocCounter(
        language=ENGLISH,
        news=fake.pyint(min_value=1),
        spam=fake.pyint(min_value=1)
    )

    return doc_counter


@pytest.fixture
async def fake_stats_db():
    with tempfile.TemporaryDirectory() as temp_path:
        temp_db_filepath = Path(temp_path) / TEST_DB_FILENAME

        original_db_filepath = stats_db.DB_FILEPATH
        stats_db.DB_FILEPATH = temp_db_filepath

        await stats_db._setup_db()

        yield stats_db

        stats_db.DB_FILEPATH = original_db_filepath


@pytest.fixture
async def fake_stats_db_with_random_doc_data(
        fake_stats_db,
        fake_eng_doc_counter
        ):
    command = f"""
        UPDATE {fake_stats_db.DOC_STATS_TABLE}
        SET news={fake_eng_doc_counter.news}, spam={fake_eng_doc_counter.spam}
        WHERE language = '{fake_eng_doc_counter.language}'
    """

    await base.execute(fake_stats_db.DB_FILEPATH, command)

    return fake_stats_db


@pytest.fixture
async def fake_stats_db_with_random_doc_and_token_data(
        fake_stats_db,
        fake_seq_token_stats
        ):
    command = f"""
        INSERT INTO {fake_stats_db.ENG_STATS_TABLE}
        VALUES (?, ?, ?)
    """

    fake_seq_token_stats_data = tuple(astuple(f) for f in fake_seq_token_stats)

    await base.execute_many(
        fake_stats_db.DB_FILEPATH,
        command,
        fake_seq_token_stats_data
    )

    return fake_stats_db