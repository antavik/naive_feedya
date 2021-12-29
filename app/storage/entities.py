import datetime

from dataclasses import dataclass, astuple
from typing import Tuple, Any


@dataclass
class TokenStats:
    token: str
    news: int
    spam: int

    def __hash__(self) -> int:
        return hash(self.token)


@dataclass
class DocCounter:
    language: str
    news: int
    spam: int


@dataclass
class FeedEntry:
    feed: str
    title: str
    url: str
    summary: str
    published_timestamp: float
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


def feed_entry_to_tuple_factory(feed_entry_list: list) -> Tuple[Any, ...]:
    return (
        feed_entry_list[0],
        feed_entry_list[1],
        feed_entry_list[2],
        feed_entry_list[3],
        feed_entry_list[4],
        feed_entry_list[5],
        feed_entry_list[6],
    )


def feed_entry_as_tuple(entry: FeedEntry) -> Tuple[Any, ...]:
    return astuple(entry, tuple_factory=feed_entry_to_tuple_factory)
