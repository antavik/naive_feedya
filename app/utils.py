import sys

import settings

from itertools import count


def configure_logging():
    from logging import Formatter, getLogger, INFO, DEBUG, StreamHandler

    logger = getLogger()

    handler = StreamHandler(sys.stdout)
    formatter = Formatter(settings.LOGGING_FORMAT, settings.LOGGING_DT_FORMAT)

    handler.setLevel(INFO)
    handler.setFormatter(formatter)

    logger.setLevel(DEBUG)
    logger.addHandler(handler)


def trim_text(text: str) -> str:
    if len(text) <= settings.SUMMARY_LIMIT:
        return text

    end_index = None

    ending = '...'
    limit_index = settings.SUMMARY_LIMIT - 1
    trimmed_limit_index = limit_index - len(ending)

    for l, i in zip(text[limit_index::-1], count(limit_index, -1)):
        if (l == ' ' or i == '.') and i <= trimmed_limit_index:
            end_index = i - 1 if text[i-1] == '.' else i

            break

    text = text[:end_index] + ending

    return text
