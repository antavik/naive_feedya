import logging
import asyncio

import httpx


class Client:

    def __init__(
            self,
            url: str,
            token: str,
            event_loop: asyncio.AbstractEventLoop,
            timeout: int = 5,
            retries: int = 3,
            retry_timeout: int = 10
    ):
        self.url = url
        self.token = token
        self.timeout = timeout
        self.event_loop = event_loop
        self.retries = retries
        self.retry_timeout = retry_timeout

        self._http_client = httpx.AsyncClient(
            base_url=self.url,
            headers={'x-user-id': self.token},
            timeout=self.timeout
        )

    async def make_readable(self, url: str) -> bytes:
        while retries := self.retries:
            try:
                response = await self._http_client.post('', json={'url': url})
                response.raise_for_status()
            except Exception as exc:
                logging.error('Error clipping url %s: %s', url, exc)

                retries -= 1
                await asyncio.sleep(self.retry_timeout)

                continue

            logging.debug('Url %s clipped', url)

            return await response.aread()

        logging.warning('Stop clipping url %s', url)

        raise Exception(exc)  # noqa

    async def close(self):
        await self._http_client.aclose()

    def __del__(self):
        self.event_loop.run_until_complete(self.close())
