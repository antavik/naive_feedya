import logging
import time
import datetime

import httpx
import feedparser as fp

import settings

from typing import Optional, Union

from feedparser import FeedParserDict

from feeds import Feed

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
    ) -> Optional[float]:
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


async def get_feed(feed: Feed) -> Union[bytes, None]:
    async with httpx.AsyncClient(headers={'user-agent': 'nf'}) as http_client:
        try:
            response = await http_client.get(
                feed.url, follow_redirects=feed.follow_redirects
            )
        except httpx.ReadTimeout as exc:
            logging.warning('Timeout exceed for feed %s, %s', feed.title, exc)

            return

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logging.error(
            'Error while getting feed %s data, %s',
            feed.title,
            exc
        )

        return
    else:
        logging.debug('Feed %s received', feed.title)

    return await response.aread()


async def parse(feed: Feed) -> tuple[list[EntryProxy], datetime.datetime]:
    feed_data = await get_feed(feed)
    parsed_dt = datetime.datetime.utcnow()

    if feed_data is None:
        parsed_entries = []
    else:
        parsed_entries = [EntryProxy(e) for e in fp.parse(feed_data).entries]

    return parsed_entries, parsed_dt
