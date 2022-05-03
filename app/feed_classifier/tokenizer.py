import string
import re

import settings
import constants

_translation_symbols = dict.fromkeys(string.punctuation + "’‘–«»")
_translation_symbols['\xa0'] = ' '
_TRANSLATION_MAPPING = str.maketrans(_translation_symbols)


if settings.APP_LANG == constants.ENGLISH:
    import nltk

    from nltk.corpus import stopwords
    from nltk.stem.porter import PorterStemmer

    nltk.download('punkt')
    nltk.download('stopwords')

    CUSTOM_FILTER = {'cnet', }

    _STEMMER = PorterStemmer()

    def tokenize_document(document: str) -> tuple[str, ...]:
        processed_document = document.translate(_TRANSLATION_MAPPING)

        tokens = tuple(
            _STEMMER.stem(word)
            for word in set(processed_document.split())
            if word not in stopwords.words(settings.APP_LANG) and
            word not in CUSTOM_FILTER and
            not re.fullmatch(r'^(19|20)\d{2}$', word)  # Regex for years 19??, 20??  # noqa
        )

        return tokens

elif settings.APP_LANG == constants.RUSSIAN:
    import spacy
    
    _LEMMER = spacy.load("ru_core_news_sm")

    def tokenize_document(document: str) -> tuple[str, ...]:
        processed_document = document.translate(_TRANSLATION_MAPPING)

        tokens = tuple(
            token.lemma_
            for token in _LEMMER(processed_document)
            if not token.is_stop and
            not re.fullmatch(r'^(19|20)\d{2}$', token.text)  # Regex for years 19??, 20??  # noqa
        )

        return tokens
