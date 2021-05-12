import asyncio
import logging

import settings

from uvicorn import Config, Server

from feeds import FEEDS
from manager import (
    process_feed,
    clean_feed_entries_db,
)
from web.app import APP
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


async def serve():
    config = Config(
        app=APP,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT
    )
    server = Server(config)

    await server.serve()


async def parse():
    logging.info('Start fetching feeds')

    while True:
        for feed in FEEDS:
            asyncio.create_task(
                process_feed(feed),
                name=f'{feed.title.capitalize()} feed procession task'
            )

        asyncio.create_task(
            clean_feed_entries_db(),
            name='DB cleaning task'
        )

        await asyncio.sleep(settings.FEED_REFRESH_TIME_SECONDS)


async def setup_dbs():
    from storage import feed_entries_db, stats_db

    await feed_entries_db._setup_db()
    await stats_db._setup_db()


if __name__ == '__main__':
    if not settings.FEED_ENTRIES_DB_FILEPATH.exists() or not settings.STATS_DB_FILEPATH.exists():  # noqa
        asyncio.run(setup_dbs())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
