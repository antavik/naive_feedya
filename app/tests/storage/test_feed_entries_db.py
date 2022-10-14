import random
import datetime

import pytest

import settings


@pytest.mark.asyncio
async def test_get__entries__success(
    fake_feed_entries_db_with_random_data,
    fake_seq_feed_entries
):
    fake_db = fake_feed_entries_db_with_random_data

    test_entry = random.choice(fake_seq_feed_entries)

    result = await fake_db.get(test_entry.url)

    assert result.url == test_entry.url


@pytest.mark.asyncio
async def test_fetch_all_entries__entries__success(
    fake_feed_entries_db_with_random_data,
    fake_seq_feed_entries
):
    fake_db = fake_feed_entries_db_with_random_data

    result = await fake_db.fetch_all_entries()

    assert len(result) == len(fake_seq_feed_entries)


@pytest.mark.asyncio
async def test_save__valid_feed_entry__success_insert(
        fake_feed_entries_db,
        fake_feed_entry
):
    await fake_feed_entries_db.save(fake_feed_entry)

    feed_entry = await fake_feed_entries_db.get(fake_feed_entry.url)

    assert feed_entry == fake_feed_entry


@pytest.mark.asyncio
async def test_exists__valid_url__exists(
        fake_feed_entries_db_with_random_data,
        fake_seq_feed_entries
):
    fake_random_feed_entry = random.choice(fake_seq_feed_entries)

    exists = await fake_feed_entries_db_with_random_data.exists(
        fake_random_feed_entry.url
    )

    assert exists


@pytest.mark.asyncio
async def test_exists__invalid_url__not_exists(
        fake_feed_entries_db_with_random_data,
        fake_feed_entry
):
    exists = await fake_feed_entries_db_with_random_data.exists(
        fake_feed_entry.url
    )

    assert not exists


@pytest.mark.asyncio
async def test_filter_exist_urls__new_urls__empty_tuple(
        fake_feed_entries_db_with_random_data,
        fake_url
):
    fake_db = fake_feed_entries_db_with_random_data

    result = await fake_db.filter_exist_urls([fake_url])

    assert not result


@pytest.mark.asyncio
async def test_filter_exist_urls__urls_from_db__urls_from_db(
        fake_feed_entries_db_with_random_data,
        fake_seq_feed_entries
):
    fake_db = fake_feed_entries_db_with_random_data
    fake_urls = [e.url for e in fake_seq_feed_entries]

    result = await fake_db.filter_exist_urls(fake_urls)

    assert sorted(result) == sorted(fake_urls)


@pytest.mark.asyncio
async def test_fetch_expired_entries_with_archived_clips__entries_with_clips__entries(  # noqa
        fake_feed_entries_db_with_random_data_older_than_days_threshold,
        fake_seq_feed_entries
):
    def sort_entries(entries):
        return sorted(entries, key=lambda e: e.archive)

    fake_db = fake_feed_entries_db_with_random_data_older_than_days_threshold
    expired_entities = [
        e for e in fake_seq_feed_entries
        if (
            (
                not e.is_classified
                or (e.is_classified and not e.is_valid)
            )
            and e.archive is not None
        )
    ]
    expired_entities = sort_entries(expired_entities)

    result = await fake_db.fetch_expired_entries_with_archived_clips()

    assert sort_entries(result) == expired_entities


@pytest.mark.asyncio
async def test_remove_expired__valid_date_delta__removed_old(
        fake_feed_entries_db_with_random_data_older_than_days_threshold,
        fake_seq_feed_entries
):
    fake_db = fake_feed_entries_db_with_random_data_older_than_days_threshold
    expired_entities = [
        e for e in fake_seq_feed_entries
        if not e.is_classified or (e.is_classified and not e.is_valid)
    ]

    removed_data = await fake_db.remove_expired()

    assert removed_data == len(expired_entities)


@pytest.mark.asyncio
async def test_fetch_last_entries__true_label__fetch_recent_news(
        fake_feed_entries_db_with_random_data_with_recent_feed_entries,
        fake_seq_feed_entries
):
    fake_db = fake_feed_entries_db_with_random_data_with_recent_feed_entries
    tracking_timestamp = (
        datetime.datetime.now() -
        datetime.timedelta(hours=settings.RECENT_FEED_ENTRIES_HOURS)
    ).timestamp()
    feeds = (e.feed for e in fake_seq_feed_entries)

    recent_entries = await fake_db.fetch_last_entries(
        feeds=feeds,
        valid=True,
        hours_delta=settings.RECENT_FEED_ENTRIES_HOURS
    )

    assert all(
        e.is_valid
        for e in recent_entries
        if e.published_timestamp > tracking_timestamp
    )


@pytest.mark.asyncio
async def test_fetch_last_entries__false_label__fetch_recent_spam(
        fake_feed_entries_db_with_random_data_with_recent_feed_entries,
        fake_seq_feed_entries
):
    fake_db = fake_feed_entries_db_with_random_data_with_recent_feed_entries
    tracking_timestamp = (
        datetime.datetime.now() -
        datetime.timedelta(hours=settings.RECENT_FEED_ENTRIES_HOURS)
    ).timestamp()
    feeds = (e.feed for e in fake_seq_feed_entries)

    recent_entries = await fake_db.fetch_last_entries(
        feeds=feeds,
        valid=False,
        hours_delta=settings.RECENT_FEED_ENTRIES_HOURS
    )

    assert all(
        not e.valid
        for e in recent_entries
        if e.published_timestamp > tracking_timestamp
    )


@pytest.mark.asyncio
async def test_update_validity__spam_url__updated_news(
        fake_feed_entries_db,
        fake_spam_entry
):
    is_news = True

    await fake_feed_entries_db.save(fake_spam_entry)

    await fake_feed_entries_db.update_validity(
        fake_spam_entry.url,
        is_news
    )

    updated_news_entry = await fake_feed_entries_db.get(
        fake_spam_entry.url
    )

    assert updated_news_entry.is_valid and updated_news_entry.is_classified


@pytest.mark.asyncio
async def test_update_validity__news_url__updated_spam(
        fake_feed_entries_db,
        fake_news_entry
):
    is_spam = False

    await fake_feed_entries_db.save(fake_news_entry)

    await fake_feed_entries_db.update_validity(
        fake_news_entry.url,
        is_spam
    )

    updated_news_entry = await fake_feed_entries_db.get(
        fake_news_entry.url
    )

    assert not updated_news_entry.is_valid and updated_news_entry.is_classified


@pytest.mark.asyncio
async def test_is_classified__valid_url__classified(
        fake_feed_entries_db_with_random_data,
        fake_feed_entry_classified
):
    fake_db = fake_feed_entries_db_with_random_data

    await fake_db.save(fake_feed_entry_classified)

    classified = await fake_db.is_classified(
        fake_feed_entry_classified.url
    )

    assert classified


@pytest.mark.asyncio
async def test_is_classified__valid_url__unclassified(
        fake_feed_entries_db_with_random_data,
        fake_feed_entry_unclassified
):
    fake_db = fake_feed_entries_db_with_random_data

    await fake_db.save(fake_feed_entry_unclassified)

    classified = await fake_db.is_classified(
        fake_feed_entry_unclassified.url
    )

    assert not classified


@pytest.mark.asyncio
async def test_is_classified__invalid_url__none(
        fake_feed_entries_db_with_random_data,
        fake_feed_entry
):
    fake_db = fake_feed_entries_db_with_random_data

    result = await fake_db.is_classified(fake_feed_entry.url)

    assert result is None


@pytest.mark.asyncio
async def test_save_many__many_feeds__row_count(
        fake_feed_entries_db,
        fake_seq_feed_entries
):
    fake_db = fake_feed_entries_db

    result = await fake_db.save_many(fake_seq_feed_entries)

    assert result == len(fake_seq_feed_entries)


@pytest.mark.asyncio
async def test_save_many__empty_list__row_count(fake_feed_entries_db):
    fake_db = fake_feed_entries_db

    result = await fake_db.save_many([])

    assert not result


@pytest.mark.asyncio
async def test_fetch_unarchived_valid_classified_entries__many_unarchived__many_entries(  # noqa
        fake_feed_entries_db_with_unarchived_data,
        fake_seq_unarchived_feed_entries
):
    fake_db = fake_feed_entries_db_with_unarchived_data

    result = await fake_db.fetch_unarchived_valid_classified_entries()

    expected_entites = [
        e
        for e in fake_seq_unarchived_feed_entries
        if e.is_valid and e.is_classified
    ]

    assert len(expected_entites) == len(result)


@pytest.mark.asyncio
async def test_fetch_unarchived_valid_classified_entries__no_unarchived__no_entries(  # noqa
        fake_feed_entries_db,
        fake_feed_entries_db_with_random_data
):
    fake_db = fake_feed_entries_db_with_random_data

    result = await fake_db.fetch_unarchived_valid_classified_entries()

    assert not result


@pytest.mark.asyncio
async def test_update_archived__archived__updated(
        fake_feed_entries_db_with_unarchived_data,
        fake_seq_unarchived_feed_entries
):
    fake_db = fake_feed_entries_db_with_unarchived_data
    test_entry = random.choice(fake_seq_unarchived_feed_entries)

    result = fake_db.update_archived(test_entry)

    assert result
