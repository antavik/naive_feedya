from typing import Callable, List, Tuple, Union, Iterable

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

        await _update_tokens(tokens, is_valid, language)


async def classify(document: str, language: str) -> bool:
    tokens = tokenize_document(document, language)

    total_p_news, total_p_spam = await stats_db.get_docs_p_values(language)

    for token in tokens:
        p_news, p_spam = await stats_db.get_token_p_values(token)

        total_p_news += p_news
        total_p_spam += p_spam

    return total_p_news > total_p_spam


async def update_stats(document: str, label: bool, language: str):
    tokens = tokenize_document(document, language)

    await _update_tokens(tokens, label, language)


async def _update_tokens(
        document_tokens: Tuple[str, ...],
        is_valid: bool,
        language: str,
    ) -> Tuple[int, int]:
    for token in document_tokens:
        if is_valid:
            updated_tokens = await stats_db.save_or_increment_news_token(token)
        else:
            updated_tokens = await stats_db.save_or_increment_spam_token(token)

    if is_valid:
        updated_docs = await stats_db.increment_doc_counter(language, 'news')
    else:
        updated_docs = await stats_db.increment_doc_counter(language, 'spam')

    return updated_tokens, updated_docs
