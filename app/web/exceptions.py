from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

InvalidCredentialsException = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail='Invalid credentials',
    headers={'WWW-Authenticate': 'Bearer'}
)

EntryURLNotFoundException = HTTPException(
    status_code=HTTP_404_NOT_FOUND,
    detail='Feed entry URL not found',
    headers={'WWW-Authenticate': 'Bearer'}
)
