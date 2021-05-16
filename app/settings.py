import os

from pathlib import Path

from starlette.datastructures import Secret

from constants import ENGLISH
from utils import str2bool

# User
USERNAME = Secret(os.environ['USERNAME'])
PASSWORD = Secret(os.environ['PASSWORD'])

# Paths
CWD = Path.cwd()

CACHE_PATH = Path(os.getenv('CACHE_PATH', '/var/lib/naive_feedya/'))
CACHE_PATH.mkdir(exist_ok=True)

DB_PATH = CACHE_PATH / 'dbs'
DB_PATH.mkdir(exist_ok=True)

FEED_ENTRIES_DB_FILENAME = 'feed_entries.sqlite'
FEED_ENTRIES_DB_FILEPATH = DB_PATH / FEED_ENTRIES_DB_FILENAME
STATS_DB_FILENAME = 'classifier.sqlite'
STATS_DB_FILEPATH = DB_PATH / STATS_DB_FILENAME

# Templates paths
TEMPLATES_FOLDER = 'web/templates'
TEMPLATES_PATH = CWD / TEMPLATES_FOLDER
BASE_TEMPLATE_FILENAME = 'base.html'
TAB_TEMPLATE_FILENAME = 'tab.html'
LOGIN_TEMPLATE_FILENAME = 'login.html'

STATIC_FOLDER = 'web/static'
STATIC_PATH = CWD / STATIC_FOLDER

# Languages
SUPPORTED_LANGUAGES = (ENGLISH,)

# Thresholds
FEED_REFRESH_TIME_SECONDS = 60 * 5
FEED_ENTRIES_DAYS_THRESHOLD = 7
RECENT_FEED_ENTRIES_HOURS = 6
TOKEN_EXPIRATION_DELTA_DAYS = 7
SUMMARY_TEXT_LIMIT = 200

# Web server
API_NAME = 'naive_feedya'
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8008

# Date time template
DT_TEMPLATE = '%b %d, %Y, %H:%M'

# Logging
LOGGING_FILE_ENABLE = str2bool(os.getenv('LOGGING_FILE_ENABLE', ''))
LOGGING_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
LOGGING_FORMAT = '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s'  # noqa
