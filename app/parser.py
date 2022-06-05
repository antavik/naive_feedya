import time
import datetime
import typing as t

import feedparser as fp

import settings

from feedparser import FeedParserDict

# Add exceptions in feed parsing sinitize filter
fp.sanitizer._HTMLSanitizer.acceptable_elements -= {'img', 'em'}


class EntryProxy:

    __slots__ = (
        'entry',
        'title',
        'url',
        'summary',
        'published_parsed',
        'update_parsed',
        'published_timestamp',
    )

    def __init__(self, entry: FeedParserDict):
        self.entry = entry
        self.title = entry.title
        self.url = entry.link
        self.summary = entry.get('summary', '')
        self.published_parsed = entry.get('published_parsed')
        self.update_parsed = entry.get('update_parsed')
        self.published_timestamp = self._define_published_timestamp(
            self.published_parsed, self.update_parsed
        )

    @property
    def under_date_threshold(self) -> bool:
        threshold_datetime = (
            datetime.datetime.now() -
            datetime.timedelta(days=settings.FEED_ENTRIES_DAYS_THRESHOLD)
        )
        threshold_timestamp = threshold_datetime.timestamp()

        if self.published_timestamp and self.published_timestamp < threshold_timestamp:  # noqa
            result = False
        else:
            result = True

        return result

    @staticmethod
    def _define_published_timestamp(
            published: time.struct_time,
            updated: time.struct_time
    ) -> t.Optional[float]:
        if published or updated:
            published_timestamp = time.mktime(published or updated)
        else:
            published_timestamp = None

        return published_timestamp

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'title={self.title}, '
            f'url={self.url}, '
            f'published_timestamp={self.published_timestamp})'
        )


def parse(data: bytes) -> list[EntryProxy]:
    return [EntryProxy(e) for e in fp.parse(data).entries]
