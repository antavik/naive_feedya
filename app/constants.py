NEWS = 'news'
SPAM = 'spam'

ENGLISH = 'english'
RUSSIAN = 'russian'

STATS_TABLES_MAPPING = {
    lang: f'{lang}_token_stats'
    for lang in (ENGLISH, RUSSIAN)
}
