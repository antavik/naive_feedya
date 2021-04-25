import logging

import settings

from typing import Callable, List, Tuple, Union

from storage import stats_db
from .tokenizer import tokenize_document


async def train(
        labeled_documents: List[Tuple[int, str]],
        label_func: Callable[[Union[int, bool]], bool],
        language: str,
        ):
    for label, document in labeled_documents:
        tokens = tokenize_document(document, language)
        is_valid = label_func(label)

        await _update_tokens_and_docs_stats(tokens, is_valid, language)


async def classify(document: str, language: str) -> bool:
    tokens = tokenize_document(document, language)

    total_p_news, total_p_spam = await stats_db.get_docs_p_values(language)

    if total_p_news is None or total_p_spam is None:
        logging.warning('%s docs stats have zero stats', language.capitalize())

        return True

    for token in tokens:
        p_news, p_spam = await stats_db.get_token_p_values(token)

        total_p_news += p_news
        total_p_spam += p_spam

    return total_p_news > total_p_spam


async def update_stats(document: str, label: bool, language: str) -> bool:
    tokens = tokenize_document(document, language)

    updated_tokens, updated_docs = await _update_tokens_and_docs_stats(
        tokens,
        label,
        language
    )

    return updated_tokens, updated_docs


async def reverse_stats(document: str, label: bool, language: str):
    tokens = tokenize_document(document, language)

    updated_tokens = await _reverse_tokens_stats(tokens, label)

    return updated_tokens


async def _update_tokens_and_docs_stats(
        document_tokens: Tuple[str, ...],
        is_valid: bool,
        language: str
        ) -> Tuple[int, int]:
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
            settings.NEWS if is_valid else settings.SPAM
        )

    return updated_tokens, updated_docs


async def _reverse_tokens_stats(
        document_tokens: Tuple[str, ...],
        is_valid: bool
        ) -> int:
    updated_tokens = 0

    if is_valid:
        new_label, old_label = settings.NEWS, settings.SPAM
    else:
        new_label, old_label = settings.SPAM, settings.NEWS

    for token in document_tokens:
        updated_tokens += await stats_db.reverse_token_stats(
            token,
            new_label,
            old_label
        )

    return updated_tokens
