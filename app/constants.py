from enum import IntEnum


class EntryType(IntEnum):
    NEWS = True
    SPAM = False


ENGLISH = 'english'
RUSSIAN = 'russian'

STATS_TABLES_MAPPING = {
    lang: f'{lang}_token_stats'
    for lang in (ENGLISH, RUSSIAN)
}
