from pathlib import Path

# Paths
CWD = Path.cwd()

BASE_CACHE_PATH = Path('/var/lib/naive_feedya/')
BASE_CACHE_PATH.mkdir(exist_ok=True)

DB_PATH = BASE_CACHE_PATH / 'dbs'
DB_PATH.mkdir(exist_ok=True)

FEED_ENTRIES_DB_FILENAME = 'feed_entries.sqlite'
FEED_ENTRIES_DB_FILEPATH = DB_PATH / FEED_ENTRIES_DB_FILENAME
STATS_DB_FILENAME = 'classifier.sqlite'
STATS_DB_FILEPATH = DB_PATH / STATS_DB_FILENAME

TEMPLATES_FOLDER = 'web/templates'
TEMPLATES_PATH = CWD / TEMPLATES_FOLDER
TEMPLATE_FILENAME = 'template.html'

# Languages
ENGLISH_LANGUAGE = 'english'
SUPPORTED_LANGUAGES = (ENGLISH_LANGUAGE,)

# Thresholds
FEED_REFRESH_TIME_SECONDS = 60 * 5
FEED_ENTRIES_DAYS_THRESHOLD = 7
RECENT_FEED_ENTRIES_HOURS = 6

# WS server
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8008

# Date time template
DT_TEMPLATE = '%b %d, %Y, %H:%M'

# Logging
LOGGING_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
LOGGING_FORMAT = '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s'

SUMMARY_LIMIT = 200

NEWS = 'news'
SPAM = 'spam'
