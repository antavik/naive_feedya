import logging
import time

import httpx
import feedparser as fp

from typing import List, Optional

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
        'published_date',
    )

    def __init__(self, entry: FeedParserDict):
        self.entry = entry
        self.title = entry.title
        self.url = entry.link
        self.summary = entry.summary
        self.published_parsed = entry.get('published_parsed')
        self.update_parsed = entry.get('update_parsed')
        self.published_date = self._define_published_date(
            self.published_parsed,
            self.update_parsed
        )

    @staticmethod
    def _define_published_date(
            published: time.struct_time,
            updated: time.struct_time
            ) -> Optional[float]:
        if published or updated:
            published_date = time.mktime(published or updated)
        else:
            published_date = None

        return published_date


async def get_feed(feed: Feed) -> bytes:
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(feed.url)

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logging.error(
            'Error while getting feed %s data: %s',
            feed.title,
            exc
        )

        feed_data = None
    else:
        logging.info('Feed %s recieved', feed.title)

        feed_data = await response.aread()

    return feed_data


async def parse(feed: Feed) -> List[EntryProxy]:
    feed_data = await get_feed(feed)

    if feed_data is None:
        parsed_entries = []
    else:
        parsed_entries = [EntryProxy(e) for e in fp.parse(feed_data).entries]

    return parsed_entries
