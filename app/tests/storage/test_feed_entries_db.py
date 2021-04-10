import random
import datetime

import pytest

import settings


@pytest.mark.asyncio
async def test_save_command__valid_feed_entry__success_insert(
        fake_feed_entries_db,
        fake_feed_entry
        ):
    await fake_feed_entries_db.save(fake_feed_entry)

    feed_entry = await fake_feed_entries_db.get(fake_feed_entry.url)

    assert feed_entry == fake_feed_entry


@pytest.mark.asyncio
async def test_exists_command__valid_url__exists(
        fake_feed_entries_db_with_random_data,
        fake_seq_feed_entries
        ):
    fake_random_feed_entry = random.choice(fake_seq_feed_entries)

    exists = await fake_feed_entries_db_with_random_data.exists(
        fake_random_feed_entry.url
    )

    assert exists


@pytest.mark.asyncio
async def test_exists_command__invalid_url__not_exists(
        fake_feed_entries_db_with_random_data,
        fake_feed_entry
        ):
    exists = await fake_feed_entries_db_with_random_data.exists(
        fake_feed_entry.url
    )

    assert not exists


@pytest.mark.asyncio
async def test_remove_old_command__valid_date_delta__removed_old(
        fake_feed_entries_db_with_random_data_older_than_days_threshold
        ):
    fake_db = fake_feed_entries_db_with_random_data_older_than_days_threshold

    await fake_db.remove_old()

    test_feed_entries = await fake_db.fetch_all_entries()

    assert not test_feed_entries


@pytest.mark.asyncio
async def test_fetch_last_entries_command__true_label__fetch_recent_news(
        fake_feed_entries_db_with_random_data_with_recent_feed_entries,
        fake_seq_feed_entries
        ):
    fake_db = fake_feed_entries_db_with_random_data_with_recent_feed_entries
    tracking_datetime = (
        datetime.datetime.now() -
        datetime.timedelta(hours=settings.RECENT_FEED_ENTRIES_HOURS)
    )
    feeds = (e.feed for e in fake_seq_feed_entries)

    recent_news = await fake_db.fetch_last_entries(
        feeds=feeds,
        valid=True,
        hours_delta=settings.RECENT_FEED_ENTRIES_HOURS
    )

    assert all(
        n.valid
        for n in recent_news
        if n.published_datetime > tracking_datetime
    )


@pytest.mark.asyncio
async def test_fetch_last_entries_command__false_label__fetch_recent_spam(
        fake_feed_entries_db_with_random_data_with_recent_feed_entries,
        fake_seq_feed_entries
        ):
    fake_db = fake_feed_entries_db_with_random_data_with_recent_feed_entries
    tracking_datetime = (
        datetime.datetime.now() -
        datetime.timedelta(hours=settings.RECENT_FEED_ENTRIES_HOURS)
    )
    feeds = (e.feed for e in fake_seq_feed_entries)

    recent_news = await fake_db.fetch_last_entries(
        feeds=feeds,
        valid=False,
        hours_delta=settings.RECENT_FEED_ENTRIES_HOURS
    )

    assert all(
        not n.valid
        for n in recent_news
        if n.published_datetime > tracking_datetime
    )


@pytest.mark.asyncio
async def test_update_validity_command__spam_url__updated_news(
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

    assert updated_news_entry.valid and updated_news_entry.classified


@pytest.mark.asyncio
async def test_update_validity_command__news_url__updated_spam(
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

    assert not updated_news_entry.valid and updated_news_entry.classified


@pytest.mark.asyncio
async def test_is_classified_command__valid_url__classified(
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
async def test_is_classified_command__valid_url__unclassified(
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
async def test_is_classified_command__invalid_url__none(
        fake_feed_entries_db_with_random_data,
        fake_feed_entry
        ):
    fake_db = fake_feed_entries_db_with_random_data

    result = await fake_db.is_classified(fake_feed_entry.url)

    assert result is None


@pytest.mark.asyncio
async def test_exist_urls__new_urls__empty_tuple(
        fake_feed_entries_db_with_random_data,
        fake_url
        ):
    fake_db = fake_feed_entries_db_with_random_data

    result = await fake_db.exist_urls([fake_url])

    assert not result


@pytest.mark.asyncio
async def test_exist_urls__urls_from_db__urls_from_db(
        fake_feed_entries_db_with_random_data,
        fake_seq_feed_entries
        ):
    fake_db = fake_feed_entries_db_with_random_data
    fake_urls = [e.url for e in fake_seq_feed_entries]

    result = await fake_db.exist_urls(fake_urls)

    assert sorted(result) == sorted(fake_urls)


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
