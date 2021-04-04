import random
import math

import pytest

import settings


@pytest.mark.asyncio
async def test_save_or_increment_news_token_command__new_token__success_insert(  # noqa
        fake_stats_db,
        fake_token
        ):
    await fake_stats_db.save_or_increment_news_token(fake_token)

    token_stats = await fake_stats_db.get_token_stats(fake_token)

    assert token_stats.news == 1 and token_stats.spam == 0


@pytest.mark.asyncio
async def test_save_or_increment_news_token_command__existing_token__success_insert(  # noqa
        fake_stats_db,
        fake_token
        ):
    new_token_count = 2

    for _ in range(new_token_count):
        await fake_stats_db.save_or_increment_news_token(fake_token)

    token_stats = await fake_stats_db.get_token_stats(fake_token)

    assert token_stats.news == new_token_count and token_stats.spam == 0


@pytest.mark.asyncio
async def test_save_or_increment_spam_token_command__new_token__success_insert(  # noqa
        fake_stats_db,
        fake_token
        ):
    await fake_stats_db.save_or_increment_spam_token(fake_token)

    token_stats = await fake_stats_db.get_token_stats(fake_token)

    assert token_stats.news == 0 and token_stats.spam == 1


@pytest.mark.asyncio
async def test_save_or_increment_spam_token_command__existing_token__success_insert(  # noqa
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
        fake_stats_db,
        fake_eng_doc_counter
        ):
    expected_p_values = (None, None)

    p_value = await fake_stats_db.get_docs_p_values(
        fake_eng_doc_counter.language
    )

    assert p_value == expected_p_values


@pytest.mark.asyncio
async def test_get_token_p_values_command__valid_db__success(
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
