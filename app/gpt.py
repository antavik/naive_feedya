import logging
import asyncio

import httpx

import settings
import utils

from pydantic import BaseModel, Field

log = logging.getLogger(settings.LOGGER_NAME)


class _Message(BaseModel):
    role: str
    content: str


class _Choice(BaseModel):
    index: int
    message: _Message
    finish_reason: str


class _Response(BaseModel):
    created: int
    model: str
    choices: list[_Choice]
    usage: dict[str, int]
    system_fingerprint: str
    id_: str = Field(..., alias='id')
    object_: str = Field(..., alias='object')

    @property
    def choice(self) -> _Choice:
        return self.choices and self.choices[0]


async def summarise(article: str) -> str:
    if not (
            settings.GPT_API_URL
            and settings.GPT_API_TOKEN
            and settings.GPT_MODEL_VER
            and settings.GPT_SUMMARY_PROMPT_TEMPLATE
    ):
        return None

    headers = {'Authorization': f'Bearer {settings.GPT_API_TOKEN}'}
    body = {
        'model': settings.GPT_MODEL_VER,
        'messages': [
            {
                'role': 'user',
                'content': settings.GPT_SUMMARY_PROMPT_TEMPLATE.format(article=article),  # noqa
            },
        ],
    }

    try:
        async with httpx.AsyncClient(headers=headers) as c:
            response = await c.post(settings.GPT_API_URL, json=body)
            response.raise_for_status()
    except Exception as exc:
        log.warning('GPT api error: %s', exc)

        return None

    log.debug('Got GPT response')

    result = _Response(**response.json())

    return result.choice.message.content