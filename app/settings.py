import os

from pathlib import Path

from starlette.datastructures import Secret

from constants import Language, STATS_TABLES_MAPPING
from utils import str2bool

DEV_MODE = str2bool(os.getenv('DEV_MODE', 'false'))

# User
if not DEV_MODE:
    USERNAME = Secret(os.environ['USERNAME'])
    PASSWORD = Secret(os.environ['PASSWORD'])
else:
    USERNAME = Secret(os.getenv('USERNAME', 'admin'))
    PASSWORD = Secret(os.getenv('PASSWORD', 'pass'))

# Language
_APP_LANG_ENV = os.getenv('APP_LANG', Language.ENG.value)
try:
    APP_LANG = Language(_APP_LANG_ENV)
except ValueError:
    raise ValueError(
        f'APP_LANG env var has not supported value {_APP_LANG_ENV}'
    )

STATS_TABLE = STATS_TABLES_MAPPING[APP_LANG]

# Paths
CWD = Path.cwd()

CACHE_PATH = Path(os.getenv('CACHE_PATH', '/var/lib/naive_feedya/'))
CACHE_PATH.mkdir(exist_ok=True)

if DEV_MODE and 'CONFIG_NAME' not in os.environ:
    CONFIG_NAME = 'test.ini'
else:
    CONFIG_NAME = os.environ['CONFIG_NAME']

CONFIG_FILEPATH = CACHE_PATH / CONFIG_NAME

DB_PATH = CACHE_PATH / 'dbs'
DB_PATH.mkdir(exist_ok=True)

FEED_ENTRIES_DB_FILENAME = 'feed_entries.sqlite'
FEED_ENTRIES_DB_FILEPATH = DB_PATH / APP_LANG.value / FEED_ENTRIES_DB_FILENAME
STATS_DB_FILENAME = 'classifier.sqlite'
STATS_DB_FILEPATH = DB_PATH / APP_LANG.value / STATS_DB_FILENAME

# Templates paths
TEMPLATES_FOLDER = 'web/templates'
TEMPLATES_PATH = CWD / TEMPLATES_FOLDER
BASE_TEMPLATE_FILENAME = 'base.html'
TAB_TEMPLATE_FILENAME = 'tab.html'
LOGIN_TEMPLATE_FILENAME = 'login.html'

STATIC_FOLDER = 'web/static'
STATIC_PATH = CWD / STATIC_FOLDER

# Thresholds
FEED_REFRESH_TIME_SECONDS = 60 * 15
FEED_REFRESH_JITTER_TIME_MINUTES = (0, 6)  # Period from-to
FEED_ENTRIES_DAYS_THRESHOLD = 7
RECENT_FEED_ENTRIES_HOURS = 6
TOKEN_EXPIRATION_DELTA_DAYS = 7
SUMMARY_TEXT_LIMIT = 200

# Web server
API_NAME = 'naive_feedya'
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8008
PATH_PREFIX = os.getenv('PATH_PREFIX', '')

# Date time template
DT_TEMPLATE = '%b %d, %Y, %H:%M'

# Logging
LOGGING_FILE_ENABLE = str2bool(os.getenv('LOGGING_FILE_ENABLE', 'false'))
LOGGING_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
LOGGING_FORMAT = '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s'  # noqa

os.environ.clear()
