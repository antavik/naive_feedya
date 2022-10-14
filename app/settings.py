import os

from pathlib import Path

from starlette.datastructures import Secret

from constants import Language, STATS_TABLES_MAPPING
from utils import to_bool

DEV_MODE = to_bool(os.getenv('DEV_MODE', 'false'))

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

DB_PATH = CACHE_PATH / APP_LANG.value / 'dbs'
DB_PATH.mkdir(parents=True, exist_ok=True)

FEED_ENTRIES_DB_FILENAME = 'feed_entries.sqlite'
FEED_ENTRIES_DB_FILEPATH = DB_PATH / FEED_ENTRIES_DB_FILENAME
STATS_DB_FILENAME = 'classifier.sqlite'
STATS_DB_FILEPATH = DB_PATH / STATS_DB_FILENAME

ARCHIVE_PATH = CACHE_PATH / APP_LANG.value / 'archive'
ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)

# Templates paths
TEMPLATES_FOLDER = 'web/templates'
TEMPLATES_PATH = CWD / TEMPLATES_FOLDER
BASE_TEMPLATE = 'base.html'
TAB_TEMPLATE = 'tab.html'
LOGIN_TEMPLATE = 'login.html'
POSITIVE_RESPONSE_TEMPLATE = 'positive_response.html'
NEGATIVE_RESPONSE_TEMPLATE = 'negative_response.html'
NAV_TABLE_TEMPLATE = 'nav_table.html'

STATIC_FOLDER = 'web/static'
STATIC_PATH = CWD / STATIC_FOLDER

# Thresholds
FEED_REFRESH_TIME_SECONDS = 60 * 15
FEED_REFRESH_JITTER_TIME_MINUTES = (0, 10)  # Period from-to
FEED_ENTRIES_DAYS_THRESHOLD = 14
RECENT_FEED_ENTRIES_HOURS = 6
TOKEN_EXPIRATION_DELTA_DAYS = 7
SUMMARY_TEXT_LIMIT = 200
ARCHIVE_REFRESH = 60 * 5

# Web server
API_NAME = 'naive_feedya'
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8008
PATH_PREFIX = os.getenv('PATH_PREFIX', '')
MOBILE_PREFIX = 'm'

# Clipper
CLIPPER_URL = os.getenv('CLIPPER_URL')
CLIPPER_TOKEN = os.getenv('CLIPPER_TOKEN')
CLIPPER_TIMEOUT = int(os.getenv('CLIPPER_TIMEOUT', 5))

# Date time template
DT_TEMPLATE = '%b %d, %Y, %H:%M'

# Logging
LOGGER_NAME = 'nf-log'

# UI configurations
DEFAULT_UI_CONFIG = {
    'ui_mode': 'default',
    'content_width': '80%',
    'line_size': 3,
    'collapse_size': 9,
    'ui_path_prefix': f'{PATH_PREFIX}'
}
DEFAULT_UI_CONFIG['entry_width'] = 100 // DEFAULT_UI_CONFIG['line_size']
MOBILE_UI_CONFIG = {
    'ui_mode': 'mobile',
    'content_width': '100%',
    'line_size': 2,
    'collapse_size': 0,
    'ui_path_prefix': f'{PATH_PREFIX}/{MOBILE_PREFIX}'
}
MOBILE_UI_CONFIG['entry_width'] = 100 // MOBILE_UI_CONFIG['line_size']

os.environ.clear()
