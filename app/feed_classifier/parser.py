import logging

import httpx
import feedparser

from feeds import Feed

# Add exceptions in feed parsing sinitize filter
feedparser.sanitizer._HTMLSanitizer.acceptable_elements -= {'img', 'em'}


async def parse(feed: Feed) -> dict:
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(feed.url)

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logging.error(
            'Error while getting feed %s data: %s',
            feed.title,
            exc,
        )

        parsed_feed_dict = {}
    else:
        logging.info('Feed %s recieved', feed.title)

        parsed_feed_dict = feedparser.parse(await response.aread())

    return parsed_feed_dict
