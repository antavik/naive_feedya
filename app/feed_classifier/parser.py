import logging

import httpx
import feedparser

from feeds import Feed

# Add exceptions in feed parsing sinitize filter
feedparser.sanitizer._HTMLSanitizer.acceptable_elements -= {'img', 'em'}


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


async def parse(feed: Feed) -> list:
    feed_data = await get_feed(feed)

    if feed_data is not None:
        parsed_feed_entries = feedparser.parse(feed_data).entries
    else:
        parsed_feed_entries = []

    return parsed_feed_entries
