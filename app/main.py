import asyncio
import logging
import datetime
import sys

try:
    import uvloop

    uvloop.install()
except:  # noqa
    pass

import settings
import utils

from uvicorn import Config, Server

from feeds import Feed, FEEDS
from manager import (
    process_feed,
    clean_feed_entries_db,
    setup_all_dbs,
)
from web.app import APP


async def main():
    asyncio.create_task(serve())
    asyncio.create_task(parse(FEEDS, settings.FEED_REFRESH_TIME_SECONDS))
    asyncio.create_task(clean(settings.FEED_REFRESH_TIME_SECONDS))


async def serve():
    config = Config(
        app=APP,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT
    )
    server = Server(config)

    await server.serve()


async def parse(feeds: list[Feed], refresh: int):
    logging.info('Start parser')

    while True:
        utils.escape_single_quote.cache_clear()
        utils.escape_double_quotes.cache_clear()

        for feed in feeds:
            asyncio.create_task(
                process_feed(feed),
                name=f'{feed.title.capitalize()} feed parser'
            )

        await asyncio.sleep(refresh)


async def clean(refresh: int):
    logging.info('Start cleaner')

    while True:
        asyncio.create_task(
            clean_feed_entries_db(),
            name='DB cleaning task'
        )

        await asyncio.sleep(refresh)


async def prepare_dbs():
    if not settings.FEED_ENTRIES_DB_FILEPATH.exists() or not settings.STATS_DB_FILEPATH.exists():  # noqa
        await setup_all_dbs()


def configure_logging():
    from logging import (
        Formatter, getLogger, INFO, DEBUG, StreamHandler, FileHandler
    )

    logger = getLogger()
    logger.setLevel(DEBUG)

    formatter = Formatter(settings.LOGGING_FORMAT, settings.LOGGING_DT_FORMAT)

    stream_handler = StreamHandler(sys.stdout)
    stream_handler.setLevel(DEBUG if settings.DEV_MODE else INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    if settings.LOGGING_FILE_ENABLE:
        datetime_now = datetime.datetime.now()
        datetime_str = datetime_now.strftime("%Y-%m-%d_%H:%M:%S")

        file_handler = FileHandler(settings.CACHE_PATH / f'{datetime_str}.log')
        file_handler.setLevel(INFO)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)


if __name__ == '__main__':
    configure_logging()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(prepare_dbs())
    loop.run_until_complete(main())
    loop.run_forever()
