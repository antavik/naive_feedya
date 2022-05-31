import logging
import asyncio

import httpx


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

    async def make_readable(self, url: str) -> bytes:
        try:
            response = await self._http_client.post('', json={'url': url})
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            logging.warning(
                'Clipper timeout exceed for %s: %s', url, exc
            )

            return b''
        except Exception as exc:
            logging.error('Error clipping url %s: %s', url, exc)

            return b''
        else:
            logging.debug('Url %s clipped', url)

        return await response.aread()

    async def close(self):
        await self._http_client.aclose()

    def __del__(self):
        asyncio.get_running_loop().run_until_complete(self.close())
