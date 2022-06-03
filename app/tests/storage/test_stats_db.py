import random
import math

import pytest

import settings

from constants import EntryType


@pytest.mark.asyncio
async def test_get_token_stats__token__token(
    fake_stats_db_with_random_doc_and_token_data,
    fake_seq_token_stats
):
    fake_db = fake_stats_db_with_random_doc_and_token_data

    test_token = random.choice(fake_seq_token_stats)

    result = await fake_db.get_token_stats(test_token.token)

    assert test_token == result


@pytest.mark.asyncio
async def test_get_token_stats__token__empty(
    fake_stats_db,
    fake_seq_token_stats
):
    fake_db = fake_stats_db

    test_token = random.choice(fake_seq_token_stats)

    result = await fake_db.get_token_stats(test_token.token)

    assert result is None


@pytest.mark.asyncio
async def test_get_doc_counter__language__counter(
    fake_stats_db_with_random_doc_data
):
    fake_db = fake_stats_db_with_random_doc_data

    result = await fake_db.get_doc_counter(settings.APP_LANG)

    assert result


@pytest.mark.asyncio
async def test_get_doc_counter__empty_table__counter(fake_stats_db):
    fake_db = fake_stats_db

    result = await fake_db.get_doc_counter(settings.APP_LANG)

    assert result.news == 0 and result.spam == 0


@pytest.mark.asyncio
async def test_save_or_increment_news_token__new_token__success_insert(
        fake_stats_db,
        fake_token
):
    await fake_stats_db.save_or_increment_news_token(fake_token)

    token_stats = await fake_stats_db.get_token_stats(fake_token)

    assert token_stats.news == 1 and token_stats.spam == 0


@pytest.mark.asyncio
async def test_save_or_increment_news_token__existing_token__success_insert(
        fake_stats_db,
        fake_token
):
    new_token_count = 2

    for _ in range(new_token_count):
        await fake_stats_db.save_or_increment_news_token(fake_token)

    token_stats = await fake_stats_db.get_token_stats(fake_token)

    assert token_stats.news == new_token_count and token_stats.spam == 0


@pytest.mark.asyncio
async def test_save_or_increment_spam_token__new_token__success_insert(
        fake_stats_db,
        fake_token
):
    await fake_stats_db.save_or_increment_spam_token(fake_token)

    token_stats = await fake_stats_db.get_token_stats(fake_token)

    assert token_stats.news == 0 and token_stats.spam == 1


@pytest.mark.asyncio
async def test_save_or_increment_spam_token__existing_token__success_insert(
        fake_stats_db,
        fake_token
):
    new_token_count = 2

    for _ in range(new_token_count):
        await fake_stats_db.save_or_increment_spam_token(fake_token)

    token_stats = await fake_stats_db.get_token_stats(fake_token)

    assert token_stats.news == 0 and token_stats.spam == new_token_count


@pytest.mark.asyncio
async def test_increment_doc_counter__increment_counters__success(
        fake_stats_db
):
    docs_qty = 1

    for _ in range(docs_qty):
        await fake_stats_db.increment_doc_counter(
            settings.APP_LANG, EntryType.NEWS.name.lower()
        )
        await fake_stats_db.increment_doc_counter(
            settings.APP_LANG, EntryType.SPAM.name.lower()
        )

    doc_count = await fake_stats_db.get_doc_counter(settings.APP_LANG)

    assert doc_count.news == 1 and doc_count.spam == 1


@pytest.mark.asyncio
async def test_get_docs_p_values__valid_db__success(
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
async def test_get_docs_p_values__empty_db__success(
        fake_stats_db,
        fake_eng_doc_counter
):
    expected_p_values = (None, None)

    p_value = await fake_stats_db.get_docs_p_values(
        fake_eng_doc_counter.language
    )

    assert p_value == expected_p_values


@pytest.mark.asyncio
async def test_get_token_p_values__valid_db__success(
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
async def test_get_tokens_p_values__valid_db__news_p_and_spam_p(
        fake_stats_db_with_random_doc_and_token_data,
        fake_seq_token_stats
):
    fake_db = fake_stats_db_with_random_doc_and_token_data

    random_seq = random.choices(
        fake_seq_token_stats,
        k=len(fake_seq_token_stats) // 2
    )

    expected_news_p = 0
    expected_spam_p = 0
    total_tokens_qty = len(fake_seq_token_stats)
    news_tokens_qty = len([s for s in fake_seq_token_stats if s.news > 0])
    spam_tokens_qty = len([s for s in fake_seq_token_stats if s.spam > 0])
    for stats in random_seq:
        expected_news_p += math.log(
            (1 + stats.news) / (total_tokens_qty + news_tokens_qty)
        )
        expected_spam_p += math.log(
            (1 + stats.spam) / (total_tokens_qty + spam_tokens_qty)
        )

    result_news_p, result_spam_p = await fake_db.get_tokens_p_values(
        [s.token for s in random_seq]
    )

    assert (expected_news_p, expected_spam_p) == (result_news_p, result_spam_p)


@pytest.mark.asyncio
async def test_reverse_news_token__news_label__success(
        fake_stats_db_with_random_doc_and_token_data,
        fake_seq_token_stats
):
    fake_db = fake_stats_db_with_random_doc_and_token_data

    token_stats = random.choice(fake_seq_token_stats)
    token_stats.news += 1
    token_stats.spam -= 1

    updated = await fake_db.reverse_token_stats(
        token_stats.token,
        EntryType.NEWS.name.lower(),
        EntryType.SPAM.name.lower()
    )

    result = await fake_db.get_token_stats(token_stats.token)

    assert (
        updated and
        (result.news, result.spam) == (token_stats.news, token_stats.spam)
    )


@pytest.mark.asyncio
async def test_reverse_docs_stats__docs_stats__success(
        fake_stats_db_with_random_doc_data,
        fake_eng_doc_counter
):
    fake_db = fake_stats_db_with_random_doc_data

    fake_eng_doc_counter.news += 1
    fake_eng_doc_counter.spam -= 1

    updated = await fake_db.reverse_docs_stats(
        EntryType.NEWS.name.lower(),
        EntryType.SPAM.name.lower(),
        fake_eng_doc_counter.language
    )

    result = await fake_db.get_doc_counter(settings.APP_LANG)

    assert (
        updated and
        (result.news, result.spam) == (fake_eng_doc_counter.news, fake_eng_doc_counter.spam)  # noqa
    )
