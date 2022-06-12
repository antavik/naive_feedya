import asyncio

try:
    import uvloop

    uvloop.install()
except:  # noqa
    pass

import settings
import constants as const
import utils
import clipper

from uvicorn import Config, Server

from log import setup_logger
from web.app import APP
from scraper import Scraper
from feeds import Feed, FEEDS
from manager import (
    process_feed,
    clean_feed_entries,
    setup_all_dbs,
    archive_classified_entities,
)

log = setup_logger()


async def main():
    scraper = Scraper(
        event_loop=asyncio.get_running_loop(),
        jitter_period=settings.FEED_REFRESH_JITTER_TIME_MINUTES
    )

    clipper_client = None
    if settings.CLIPPER_URL is not None and settings.CLIPPER_TOKEN is not None:
        clipper_client = clipper.Client(
            url=settings.CLIPPER_URL,
            token=settings.CLIPPER_TOKEN,
            timeout=settings.CLIPPER_TIMEOUT,
            event_loop=asyncio.get_running_loop()
        )

    asyncio.create_task(serve())
    asyncio.create_task(proc(FEEDS, scraper, settings.FEED_REFRESH_TIME_SECONDS))  # noqa
    asyncio.create_task(clean(settings.FEED_REFRESH_TIME_SECONDS))
    asyncio.create_task(archive(clipper_client, settings.ARCHIVE_REFRESH))


async def serve():
    config = Config(
        app=APP,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT
    )
    server = Server(config)

    await server.serve()


async def proc(feeds: list[Feed], scraper: Scraper, refresh: int):
    log.info('Start processor')

    while True:
        utils.escape_single_quote.cache_clear()
        utils.escape_double_quotes.cache_clear()

        for feed in feeds:
            asyncio.create_task(
                process_feed(feed, scraper),
                name=f'{feed.title.capitalize()} feed parser'
            )

        await asyncio.sleep(refresh)


async def clean(refresh: int):
    log.info('Start cleaner')

    while True:
        if const.CLEANER_TASK_NAME not in {f.get_name() for f in asyncio.all_tasks()}:  # noqa
            asyncio.create_task(
                clean_feed_entries(),
                name=const.CLEANER_TASK_NAME
            )
        else:
            log.warning('Cleaner session skipped: still processing')

        await asyncio.sleep(refresh)


async def archive(clipper: None | clipper.Client, refresh: int):
    if clipper is None:
        return

    log.info('Start archiver')

    while True:
        if const.ARCHIVE_TASK_NAME not in {f.get_name() for f in asyncio.all_tasks()}:  # noqa
            asyncio.create_task(
                archive_classified_entities(clipper),
                name=const.ARCHIVE_TASK_NAME
            )
        else:
            log.warning('Archiver session skipped: still processing')

        await asyncio.sleep(refresh)


async def prepare_dbs():
    if not settings.FEED_ENTRIES_DB_FILEPATH.exists() or not settings.STATS_DB_FILEPATH.exists():  # noqa
        await setup_all_dbs()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(prepare_dbs())
    loop.run_until_complete(main())
    loop.run_forever()
