import string
import re

import nltk

from typing import Tuple

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

nltk.download('punkt')
nltk.download('stopwords')

CUSTOM_FILTER = {'cnet', }
_TRANSLATION_MAPPING = str.maketrans(
    dict.fromkeys(string.punctuation + "’‘–")
)
_STEMMER = PorterStemmer()


def tokenize_document(
        document: str,
        language: str
) -> Tuple[str, ...]:
    processed_document = document.translate(_TRANSLATION_MAPPING).lower()

    tokens = tuple(
        _STEMMER.stem(word)
        for word in set(processed_document.split())
        if word not in stopwords.words(language)
        and word not in CUSTOM_FILTER
        and not re.fullmatch(r'^(19|20)\d{2}$', word)  # Regex for years 19??, 20??  # noqa
    )

    return tokens
