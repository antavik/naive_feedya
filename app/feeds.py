import logging
import configparser

import constants as const

from dataclasses import dataclass
from typing import Optional
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
    base_url: Optional[str] = None

    def __post_init__(self):
        if not self.url.startswith('https') and not self.allow_http:
            raise ValueError('Feed url scheme should be https')

        if self.base_url is None:
            parsed_url = urlparse(self.url)

            # black magic for frozen dataclass attr assignment
            object.__setattr__(
                self, 'base_url', f'{parsed_url.scheme}://{parsed_url.netloc}'
            )

        if not self.base_url.startswith('https') and not self.allow_http:
            raise ValueError('base_url scheme should be https')


def read_feeds_config(filepath: Path, language: const.Language) -> list[Feed]:
    with filepath.open(encoding='utf-8') as f:
        cp = configparser.ConfigParser(default_section=None)
        cp.read_file(f)

    feeds = []
    for section, config in cp.items():
        if section is None:
            continue

        if config['language'] != language.value:
            logging.warning(
                'Section %s skipped because of invalid language configuration',
                section
            )

            continue

        try:
            feed = Feed(
                title=section,
                url=config['url'],
                language=language,
                skip_summary=config.getboolean('skip_summary', fallback=False),
                follow_redirects=config.getboolean('follow_redirects', fallback=False),  # noqa
                base_url=config.get('base_url')
            )
        except ValueError as e:
            logging.warning(
                'Section %s skipped of invalid url schema, %s', section, e
            )
        else:
            feeds.append(feed)

    return feeds
