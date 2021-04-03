import tempfile
import datetime
import random

import pytest

import settings

from pathlib import Path
from dataclasses import astuple

from faker import Faker

from storage import (
    FeedEntry,
    DocCounter,
    TokenStats,
    base,
    feed_entries_db,
    stats_db,
    feed_entry_tuple_factory,
)

TEST_DB_FILENAME = 'temp_db.sqlite'
TEST_DB_ROWS_COUNT = 20

fake = Faker()
Faker.seed(TEST_DB_ROWS_COUNT)


@pytest.fixture
def fake_feed_entry():
    fake_entry = FeedEntry(
        fake.company(),
        'Test_title',
        fake.uri(),
        'Test_summary',
        fake.unix_time(),
        int(fake.pybool()),
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
            fake.company(),
            'Test_title-{}'.format(i),
            fake.uri(),
            'Test_summary-{}'.format(i),
            fake.unix_time(),
            int(fake.pybool()),
            int(fake.pybool()),
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
        astuple(f, tuple_factory=feed_entry_tuple_factory)
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
        fake_seq_feed_entries
        ):
    command = f"""
        INSERT INTO {fake_feed_entries_db.FEED_ENTRIES_TABLE}
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    test_days_threshold = settings.FEED_ENTRIES_DAYS_THRESHOLD + 1
    test_timestamp = (
        datetime.datetime.now() - datetime.timedelta(days=test_days_threshold)
    ).timestamp()

    for feed_entry in fake_seq_feed_entries:
        feed_entry.published_timestamp = test_timestamp

    fake_seq_feed_entries_data = (
        astuple(f, tuple_factory=feed_entry_tuple_factory)
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
        fake_seq_feed_entries
        ):
    command = f"""
        INSERT INTO {fake_feed_entries_db.FEED_ENTRIES_TABLE}
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    half_row_count = TEST_DB_ROWS_COUNT // 2

    recent_feed_entries_timestamp = datetime.datetime.now().timestamp()

    for i in range(TEST_DB_ROWS_COUNT):
        if i < half_row_count:
            fake_seq_feed_entries[i].published_timestamp = recent_feed_entries_timestamp  # noqa
            fake_seq_feed_entries[i].valid = True
        else:
            fake_seq_feed_entries[i].published_timestamp = recent_feed_entries_timestamp  # noqa
            fake_seq_feed_entries[i].valid = False

    fake_seq_feed_entries_data = (
        astuple(f, tuple_factory=feed_entry_tuple_factory)
        for f in fake_seq_feed_entries
    )

    await base.execute_many(
        fake_feed_entries_db.DB_FILEPATH,
        command,
        fake_seq_feed_entries_data
    )

    return fake_feed_entries_db


@pytest.fixture
async def fake_token():
    return fake.color()  # Same like token


@pytest.fixture
async def fake_token_stats(fake_token):
    return TokenStats(
        fake_token,
        fake.pyint(),
        fake.pyint()
    )


@pytest.fixture
async def fake_seq_token_stats():
    token_stats = {
        TokenStats(
            fake.color(),  # Same like token
            fake.pyint(),
            fake.pyint(min_value=1),
        )
        for _ in range(TEST_DB_ROWS_COUNT)
    }

    return list(token_stats)


@pytest.fixture
async def fake_eng_doc_counter():
    news_doc_counter = fake.pyint(min_value=1)
    spam_doc_counter = fake.pyint(min_value=1)

    doc_counter = DocCounter(
        settings.ENGLISH_LANGUAGE,
        news_doc_counter,
        spam_doc_counter,
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


@pytest.fixture
def fake_text_less_than_summary_limit():
    max_text_length = random.randint(
        settings.SUMMARY_LIMIT // 2,
        settings.SUMMARY_LIMIT
    )

    return fake.text(max_nb_chars=max_text_length)


@pytest.fixture
def fake_text_more_than_summary_limit():
    max_text_length = random.randint(
        settings.SUMMARY_LIMIT + 1,
        settings.SUMMARY_LIMIT * 2
    )

    return fake.text(max_nb_chars=max_text_length)


@pytest.fixture
def datetime_now():
    return datetime.datetime.now()


@pytest.fixture
def fake_feed_type():
    return 'fake_feed_type'


@pytest.fixture
def fake_string():
    return fake.word()
