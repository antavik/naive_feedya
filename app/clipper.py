import logging
import asyncio

import httpx


class ClippingError(Exception):
    pass


class Client:

    def __init__(
            self,
            url: str,
            token: str,
            event_loop: asyncio.AbstractEventLoop,
            timeout: int = 10,
            retries: int = 3,
            retry_timeout: int = 10
    ):
        self.url = url
        self.token = token
        self.timeout = timeout
        self.event_loop = event_loop

        if retries < 1:
            raise ValueError('retries argument should be greater or equal 1')
        self.retries = retries
        self.retry_timeout = retry_timeout

        self._http_client = httpx.AsyncClient(
            base_url=self.url,
            headers={'x-user-id': self.token},
            timeout=self.timeout
        )

    async def make_readable(self, url: str) -> bytes:
        exception = None

        for _ in range(self.retries):
            try:
                response = await self._http_client.post('', json={'url': url})
                response.raise_for_status()
            except Exception as exc:
                exception = exc

                logging.warning('Error clipping url %s: %s', url, exc)

                await asyncio.sleep(self.retry_timeout)
            else:
                logging.debug('Url %s clipped', url)

                return await response.aread()

        logging.warning('Stop clipping url %s', url)

        raise ClippingError(exception)

    async def close(self):
        await self._http_client.aclose()

    def __del__(self):
        self.event_loop.run_until_complete(self.close())
