from typing import Annotated, TYPE_CHECKING
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlmodel.ext.asyncio.session import AsyncSession

from quickbot.auth.jwt import decode_access_token
from quickbot.db import get_db
from quickbot.model.user import UserBase

if TYPE_CHECKING:
    from quickbot import QuickBot

security_scheme = HTTPBearer(
    scheme_name="bearerAuth",
    bearerFormat="JWT",
)


async def get_current_user(
    request: Request,
    db_session: Annotated[AsyncSession, Depends(get_db)],
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> UserBase:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        app: QuickBot = request.app
        user = await app.user_class.get(
            session=db_session,
            id=int(user_id),
        )
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
