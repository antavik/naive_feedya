import asyncio
import logging

import settings

from feeds import FEEDS
from manager import (
    process_feed,
    clean_feed_entries_db,
)
from web.app import app
from utils import configure_logging

try:
    import uvloop

    uvloop.install()
except:  # noqa
    pass


configure_logging()


async def main():
    asyncio.create_task(serve())
    asyncio.create_task(parse())


async def parse():
    logging.info('Start fetching feeds')

    while True:
        for feed in FEEDS:
            asyncio.create_task(process_feed(feed))

        asyncio.create_task(clean_feed_entries_db())

        await asyncio.sleep(settings.FEED_REFRESH_TIME_SECONDS)


async def serve():
    from uvicorn import Config, Server

    config = Config(
        app=app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT
    )
    server = Server(config)

    await server.serve()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
