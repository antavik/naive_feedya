import datetime

from constants import Language
from dataclasses import dataclass, astuple
from typing import Any


@dataclass
class TokenStats:
    token: str
    news: int
    spam: int

    def __hash__(self) -> int:
        return hash(self.token)


@dataclass
class DocCounter:
    language: Language
    news: int
    spam: int


@dataclass
class FeedEntry:
    feed: str
    title: str
    url: str
    summary: str
    published_timestamp: float
    parsed_timestamp: float
    valid: int
    classified: int = 0

    @property
    def is_valid(self):
        return bool(self.valid)

    @property
    def is_classified(self):
        return bool(self.classified)

    @property
    def published_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.published_timestamp)


def feed_entry_to_tuple_factory(feed_entry_list: list) -> tuple[Any, ...]:
    return (
        feed_entry_list[0],  # feed
        feed_entry_list[1],  # title
        feed_entry_list[2],  # url
        feed_entry_list[3],  # summary
        feed_entry_list[4],  # published_timestamp
        feed_entry_list[5],  # parsed_timestamp
        feed_entry_list[6],  # valid
        feed_entry_list[7],  # classified
    )


def feed_entry_as_tuple(entry: FeedEntry) -> tuple[Any, ...]:
    return astuple(entry, tuple_factory=feed_entry_to_tuple_factory)
