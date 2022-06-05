import typing as t

import configparser

import constants as const
import settings

from dataclasses import dataclass
from urllib.parse import urlparse
from pathlib import Path


@dataclass(frozen=True)
class Feed:
    title: str
    url: str
    language: const.Language
    skip_summary: bool = False
    follow_redirects: bool = False
    allow_http: bool = False
    base_url: t.Optional[str] = None


def _read_feeds_config(filepath: Path, language: const.Language) -> list[Feed]:
    with filepath.open(encoding='utf-8') as f:
        cp = configparser.ConfigParser(default_section=None)
        cp.read_file(f)

    feeds = []
    for section, config in cp.items():
        if section is None:
            continue

        allow_http = config.getboolean('allow_http', fallback=False)

        feed_language = config['language']
        if feed_language != language.value:
            raise ValueError(f'Invalid language settings for {section}')

        url = config['url']
        if not url.startswith('https') and not allow_http:
            raise ValueError(f'Invalid feed url schema for {section}')

        base_url = config.get('base_url')
        if base_url is None:
            parsed_url = urlparse(url)
            base_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

        if not base_url.startswith('https') and not allow_http:
            raise ValueError(f'Invalid base_url scheme for {section}')

        skip_summary = config.getboolean('skip_summary', fallback=False)
        follow_redirects = config.getboolean('follow_redirects', fallback=False)  # noqa

        feeds.append(Feed(
            title=section,
            url=url,
            language=language,
            skip_summary=skip_summary,
            follow_redirects=follow_redirects,
            allow_http=allow_http,
            base_url=base_url
        ))

    return feeds


FEEDS = _read_feeds_config(settings.CONFIG_FILEPATH, settings.APP_LANG)
FEEDS_REGISTRY = {f.title: f for f in FEEDS}
