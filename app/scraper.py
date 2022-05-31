import logging
import asyncio
import datetime

import httpx

from typing import Union

from feeds import Feed


class Scraper:

    def __init__(self):
        self.agent = 'nf'
        self.headers = {
            'user-agent': self.agent,
        }

        self._http_client = httpx.AsyncClient(headers=self.headers)

    async def get(self, feed: Feed) -> tuple[bytes, Union[datetime.datetime, None]]:
        try:
            response = await self._http_client.get(
                feed.url, follow_redirects=feed.follow_redirects
            )
            response.raise_for_status()
        except httpx.ReadTimeout:
            logging.warning('Scraper timeout exceed for feed %s', feed.title)

            return (b'', None)
        except Exception as exc:
            logging.error(
                'Error getting feed %s data: %s', feed.title, exc
            )

            return (b'', None)
        else:
            dt_now = datetime.datetime.utcnow()

            logging.debug('Feed %s received', feed.title)

        return (await response.aread(), dt_now)

    async def close(self):
        await self._http_client.aclose()

    def __del__(self):
        asyncio.get_running_loop().run_until_complete(self.close())
