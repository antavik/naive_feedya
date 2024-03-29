import logging
import typing as t

import utils
import constants as const
import settings

from storage import stats_db
from constants import EntryType, Language
from .tokenizer import tokenize_document

log = logging.getLogger(settings.LOGGER_NAME)


async def train(
        labeled_documents: list[tuple[int, str]],
        label_func: t.Callable[[int | bool], bool],
        language: str,
):
    for label, document in labeled_documents:
        tokens = tokenize_document(document)
        is_valid = label_func(label)

        await _update_tokens_and_docs_stats(tokens, is_valid, language)


async def classify(document: str, language: const.Language) -> bool:
    tokens = tokenize_document(document)

    total_p_news, total_p_spam = await stats_db.get_docs_p_values(language)

    if total_p_news is None or total_p_spam is None:
        log.warning(
            '%s docs stats have zero stats', language.value.capitalize()
        )

        return True

    tokens_p_news, token_p_spam = await stats_db.get_tokens_p_values(tokens)
    total_p_news += tokens_p_news
    total_p_spam += token_p_spam

    return total_p_news > total_p_spam


async def update_stats(
        document: str,
        label: bool,
        language: str
) -> tuple[int, int]:
    tokens = tokenize_document(document)
    language = Language(language)

    updated_tokens, updated_docs = await _update_tokens_and_docs_stats(
        tokens, label, language
    )

    return updated_tokens, updated_docs


async def reverse_stats(
        document: str,
        label: bool,
        language: Language
) -> tuple[int, int]:
    tokens = tokenize_document(document)
    language = Language(language)

    updated_tokens, updated_docs = await _reverse_stats(
        tokens, label, language
    )

    return updated_tokens, updated_docs


async def _update_tokens_and_docs_stats(
        document_tokens: tuple[str, ...],
        is_valid: bool,
        language: Language
) -> tuple[int, int]:
    updated_tokens = 0
    updated_docs = 0

    for token in document_tokens:
        if is_valid:
            updated_tokens += await stats_db.save_or_increment_news_token(token)  # noqa
        else:
            updated_tokens += await stats_db.save_or_increment_spam_token(token)  # noqa

    if updated_tokens:
        updated_docs = await stats_db.increment_doc_counter(
            language,
            utils.lower(EntryType(is_valid).name)
        )

    return updated_tokens, updated_docs


async def _reverse_stats(
        document_tokens: tuple[str, ...],
        is_valid: bool,
        language: Language
) -> tuple[int, int]:
    updated_tokens = 0
    updated_docs = 0

    if is_valid:
        new_label, old_label = (utils.lower(EntryType.NEWS.name), utils.lower(EntryType.SPAM.name))  # noqa
    else:
        new_label, old_label = (utils.lower(EntryType.SPAM.name), utils.lower(EntryType.NEWS.name))  # noqa

    for token in document_tokens:
        updated_tokens += await stats_db.reverse_token_stats(
            token, new_label, old_label
        )

    if updated_tokens:
        updated_docs = await stats_db.reverse_docs_stats(
            new_label, old_label, language
        )

    return updated_tokens, updated_docs
