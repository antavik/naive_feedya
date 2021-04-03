import random
import datetime
import math

import pytest

import settings


class TestFeedEntriesStorage:

    @pytest.mark.asyncio
    async def test_save_command__valid_feed_entry__success_insert(
            self,
            fake_feed_entries_db,
            fake_feed_entry
        ):
        result_row_count = await fake_feed_entries_db.save(fake_feed_entry)

        feed_entry = await fake_feed_entries_db.get(fake_feed_entry.url)

        assert result_row_count == 1
        assert feed_entry == fake_feed_entry

    @pytest.mark.asyncio
    async def test_exists_command__valid_url__exists(
            self,
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
            self,
            fake_feed_entries_db_with_random_data,
            fake_feed_entry
        ):
        exists = await fake_feed_entries_db_with_random_data.exists(
            fake_feed_entry.url
        )

        assert not exists

    @pytest.mark.asyncio
    async def test_remove_old_command__valid_date_delta__removed_old(
            self,
            fake_feed_entries_db_with_random_data_older_than_days_threshold
        ):
        fake_db = fake_feed_entries_db_with_random_data_older_than_days_threshold

        await fake_db.remove_old()

        test_feed_entries = await fake_db.fetch_all_entries()

        assert not test_feed_entries

    @pytest.mark.asyncio
    async def test_fetch_last_entries_command__true_label__fetch_recent_news(
            self,
            fake_feed_entries_db_with_random_data_with_recent_feed_entries
        ):
        fake_db = fake_feed_entries_db_with_random_data_with_recent_feed_entries
        tracking_datetime = (
            datetime.datetime.now() - 
            datetime.timedelta(hours=settings.RECENT_FEED_ENTRIES_HOURS)
        )

        recent_news = await fake_db.fetch_last_entries(
            True,
            settings.RECENT_FEED_ENTRIES_HOURS
        )

        assert all(
            n.valid
            for n in recent_news
            if n.published_datetime > tracking_datetime
        )

    @pytest.mark.asyncio
    async def test_fetch_last_entries_command__false_label__fetch_recent_spam(
            self,
            fake_feed_entries_db_with_random_data_with_recent_feed_entries
        ):
        fake_db = fake_feed_entries_db_with_random_data_with_recent_feed_entries
        tracking_datetime = (
            datetime.datetime.now() - 
            datetime.timedelta(hours=settings.RECENT_FEED_ENTRIES_HOURS)
        )

        recent_news = await fake_db.fetch_last_entries(
            False,
            settings.RECENT_FEED_ENTRIES_HOURS
        )

        assert all(
            not n.valid
            for n in recent_news
            if n.published_datetime > tracking_datetime
        )

    @pytest.mark.asyncio
    async def test_update_validity_command__spam_url__updated_news(
            self,
            fake_feed_entries_db,
            fake_spam_entry
        ):
        is_news = True

        await fake_feed_entries_db.save(fake_spam_entry)

        await fake_feed_entries_db.update_validity(fake_spam_entry.url, is_news)

        updated_news_entry = await fake_feed_entries_db.get(fake_spam_entry.url)

        assert updated_news_entry.valid and updated_news_entry.classified

    @pytest.mark.asyncio
    async def test_update_validity_command__news_url__updated_spam(
            self,
            fake_feed_entries_db,
            fake_news_entry
        ):
        is_spam = False

        await fake_feed_entries_db.save(fake_news_entry)

        await fake_feed_entries_db.update_validity(fake_news_entry.url, is_spam)

        updated_news_entry = await fake_feed_entries_db.get(fake_news_entry.url)

        assert not updated_news_entry.valid and updated_news_entry.classified

    @pytest.mark.asyncio
    async def test_is_classified_command__valid_url__classified(
            self,
            fake_feed_entries_db_with_random_data,
            fake_feed_entry_classified
        ):
        fake_db = fake_feed_entries_db_with_random_data

        await fake_db.save(fake_feed_entry_classified)

        classified = await fake_db.is_classified(fake_feed_entry_classified.url)

        assert classified

    @pytest.mark.asyncio
    async def test_is_classified_command__valid_url__unclassified(
            self,
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
            self,
            fake_feed_entries_db_with_random_data,
            fake_feed_entry
        ):
        fake_db = fake_feed_entries_db_with_random_data

        result = await fake_db.is_classified(fake_feed_entry.url)

        assert result is None


class TestStatsSotrage:

    @pytest.mark.asyncio
    async def test_save_or_increment_news_token_command__new_token__success_insert(
            self,
            fake_stats_db,
            fake_token
        ):
        await fake_stats_db.save_or_increment_news_token(fake_token)

        token_stats = await fake_stats_db.get_token_stats(fake_token)

        assert token_stats.news == 1 and token_stats.spam == 0

    @pytest.mark.asyncio
    async def test_save_or_increment_news_token_command__existing_token__success_insert(
            self,
            fake_stats_db,
            fake_token
        ):
        new_token_count = 2

        for _ in range(new_token_count):
            await fake_stats_db.save_or_increment_news_token(fake_token)

        token_stats = await fake_stats_db.get_token_stats(fake_token)

        assert token_stats.news == new_token_count and token_stats.spam == 0

    @pytest.mark.asyncio
    async def test_save_or_increment_spam_token_command__new_token__success_insert(
            self,
            fake_stats_db,
            fake_token
        ):
        await fake_stats_db.save_or_increment_spam_token(fake_token)

        token_stats = await fake_stats_db.get_token_stats(fake_token)

        assert token_stats.news == 0 and token_stats.spam == 1

    @pytest.mark.asyncio
    async def test_save_or_increment_spam_token_command__existing_token__success_insert(
            self,
            fake_stats_db,
            fake_token
        ):
        new_token_count = 2

        for _ in range(new_token_count):
            await fake_stats_db.save_or_increment_spam_token(fake_token)

        token_stats = await fake_stats_db.get_token_stats(fake_token)

        assert token_stats.news == 0 and token_stats.spam == new_token_count

    @pytest.mark.asyncio
    async def test_increment_doc_counter_command__increment_counters__success(
            self,
            fake_stats_db
        ):
        docs_qty = 1
        language = settings.ENGLISH_LANGUAGE

        for _ in range(docs_qty):
            await fake_stats_db.increment_doc_counter(language, 'news')
            await fake_stats_db.increment_doc_counter(language, 'spam')

        doc_count = await fake_stats_db.get_doc_counter(language)

        assert doc_count.news == 1 and doc_count.spam == 1

    @pytest.mark.asyncio
    async def test_get_docs_p_values_command__valid_db__success(
            self,
            fake_stats_db_with_random_doc_data,
            fake_eng_doc_counter
        ):
        doc_count = fake_eng_doc_counter
        expected_p_values = (
            math.log(doc_count.news / (doc_count.news + doc_count.spam)),
            math.log(doc_count.spam / (doc_count.news + doc_count.spam)),
        )

        p_value = await fake_stats_db_with_random_doc_data.get_docs_p_values(
            fake_eng_doc_counter.language
        )

        assert p_value == expected_p_values

    @pytest.mark.asyncio
    async def test_get_docs_p_values_command__empty_db__success(
            self,
            fake_stats_db,
            fake_eng_doc_counter
        ):
        doc_count = fake_eng_doc_counter
        expected_p_values = (None, None)

        p_value = await fake_stats_db.get_docs_p_values(
            fake_eng_doc_counter.language
        )

        assert p_value == expected_p_values

    @pytest.mark.asyncio
    async def test_get_token_p_values_command__valid_db__success(
            self,
            fake_stats_db_with_random_doc_and_token_data,
            fake_seq_token_stats
        ):
        fake_db = fake_stats_db_with_random_doc_and_token_data

        random_token = random.choice(fake_seq_token_stats)
        total_tokens_qty = len(fake_seq_token_stats)
        news_tokens_qty = len([t for t in fake_seq_token_stats if t.news > 0])
        spam_tokens_qty = len([t for t in fake_seq_token_stats if t.spam > 0])

        token_news_p_value = math.log(
            (1 + random_token.news) / (total_tokens_qty + news_tokens_qty)
        )
        token_spam_p_value = math.log(
            (1 + random_token.spam) / (total_tokens_qty + spam_tokens_qty)
        )

        token_p_values = await fake_db.get_token_p_values(random_token.token)

        assert (token_news_p_value, token_spam_p_value) == token_p_values

    @pytest.mark.asyncio
    async def test_reverse_news_token_command__news_label__success(
            self,
            fake_stats_db_with_random_doc_and_token_data,
            fake_seq_token_stats
        ):
        fake_db = fake_stats_db_with_random_doc_and_token_data

        token_stats = random.choice(fake_seq_token_stats)
        token_stats.news += 1
        token_stats.spam -= 1

        await fake_db.reverse_token_stats(token_stats.token, 'news', 'spam')

        result = await fake_db.get_token_stats(token_stats.token)

        assert (
            (result.news, result.spam) == (token_stats.news, token_stats.spam)
        )
