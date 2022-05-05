import logging
import configparser

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
from pathlib import Path


@dataclass(frozen=True)
class Feed:
    title: str
    url: str
    language: str
    # classify: bool = True
    skip_summary: bool = False
    base_url: Optional[str] = None

    def __post_init__(self):
        if not self.url.startswith('https://'):
            raise ValueError(
                f'Invalid url scheme for feed {self.title}, should be https'
            )

        if self.base_url is None:
            parsed_url = urlparse(self.url)

            # black magic for frozen dataclass attr assignment
            object.__setattr__(
                self, 'base_url', f'{parsed_url.scheme}://{parsed_url.netloc}'
            )

        if not self.base_url.startswith('https://'):
            raise ValueError(
                f'Invalid base_url scheme for feed {self.title}, should be https'  # noqa
            )


def read_feeds_config(filepath: Path, language: str) -> list[Feed, ...]:
    logging.info('Reading config file %s', filepath)

    with filepath.open(encoding='utf-8') as f:
        cp = configparser.ConfigParser(default_section=None)
        cp.read_file(f)

    feeds = []
    for section, config in cp.items():
        if section is None:
            continue

        if config['language'] != language:
            logging.warning(
                'Section %s skipped because of invalid language for app configuration',  # noqa
                config['language']
            )

            continue

        feeds.append(Feed(
            title=section,
            url=config['url'],
            language=config['language'],
            skip_summary=config.getboolean('skip_summary', fallback=False),
            base_url=config.get('base_url')
        ))

    return feeds
