from fastapi import HTTPException
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

InvalidCredentials = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail='Invalid credentials',
    headers={'WWW-Authenticate': 'Bearer'}
)

FeedTypeNotFound = HTTPException(
    status_code=HTTP_404_NOT_FOUND,
    detail='Feed type not found',
    headers={'WWW-Authenticate': 'Bearer'}
)

InternalServerError = HTTPException(
    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Feed type not found',
    headers={'WWW-Authenticate': 'Bearer'}
)
