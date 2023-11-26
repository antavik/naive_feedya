import logging
import asyncio
import json

import httpx

import settings
import utils

log = logging.getLogger(settings.LOGGER_NAME)


class ClippingError(Exception):
    pass


class _Client:

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

                log.warning('Error clipping url %s: %s', url, exc)

                await asyncio.sleep(self.retry_timeout)
            else:
                log.debug('Url %s clipped', url)

                return await response.aread()

        log.warning('Stop clipping url %s', url)

        raise ClippingError(exception)

    async def close(self):
        await self._http_client.aclose()

    def __del__(self):
        self.event_loop.run_until_complete(self.close())


_CLIENT: _Client | None = None


def build(
        url: str,
        token: str,
        event_loop: asyncio.AbstractEventLoop,
        timeout: int = 10,
        retries: int = 3,
        retry_timeout: int = 10
) -> _Client:
    global _CLIENT

    _CLIENT = _Client(
        url=url,
        token=token,
        event_loop=event_loop,
        timeout=timeout,
        retries=retries,
        retry_timeout=retry_timeout,
    )

    return _CLIENT


async def make_readable_text(url: str) -> str:
    global _CLIENT

    if _CLIENT is None:
        log.warning('Clipper client not initialized')
        return

    try:
        result = await _CLIENT.make_readable(url)
    except Exception:
        return ''

    data = json.loads(result.decode())

    return data['textContent']
