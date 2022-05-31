from enum import IntEnum, Enum


class EntryType(IntEnum):
    NEWS = True
    SPAM = False


class Language(Enum):
    ENG = 'english'
    RUS = 'russian'


STATS_TABLES_MAPPING = {lang: f'{lang.value}_token_stats' for lang in Language}

CLEANER_TASK_NAME = 'Cleaner_task'
ARCHIVE_TASK_NAME = 'Archive_task'
