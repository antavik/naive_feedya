import httpx
import logging
import asyncio

from typing import Union


class Client:

    def __init__(
            self,
            url: str,
            token: str,
            timeout: int = 5
    ):
        self.url = url
        self.token = token
        self.timeout = timeout

        self._http_client = httpx.AsyncClient(
            base_url=self.url,
            headers={'x-user-id': self.token},
            timeout=self.timeout
        )

    async def make_readable(self, url: str) -> Union[None, bytes]:
        response = await self._http_client.get('', params={'url': url})

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logging.error('Error clipping url %s %s', url, exc)

            return
        else:
            logging.debug('Url %s clipped', url)

        return await response.aread()

    async def close(self):
        await self._http_client.aclose()

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self.close())
