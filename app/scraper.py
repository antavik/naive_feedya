import logging
import asyncio
import datetime

import httpx

import settings

from feeds import Feed

log = logging.getLogger(settings.LOGGER_NAME)


class Scraper:

    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.event_loop = event_loop

        self.agent = 'nf'
        self.headers = {
            'user-agent': self.agent,
        }

        self._http_client = httpx.AsyncClient(headers=self.headers)

    async def get(
            self,
            feed: Feed
    ) -> tuple[bytes, datetime.datetime | None]:
        try:
            response = await self._http_client.get(
                feed.url, follow_redirects=feed.follow_redirects
            )
            response.raise_for_status()
        except httpx.TimeoutException:
            log.warning('Scraper timeout exceed for feed %s', feed.title)

            return (b'', None)
        except Exception as exc:
            log.error('Error getting feed %s data: %s', feed.title, exc)

            return (b'', None)
        else:
            dt_now = datetime.datetime.utcnow()

            log.debug('Feed %s received', feed.title)

        return (await response.aread(), dt_now)

    async def close(self):
        await self._http_client.aclose()

    def __del__(self):
        self.event_loop.run_until_complete(self.close())
