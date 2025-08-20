from aiogram.types import Update
from fastapi import APIRouter, Request, Response, Depends, HTTPException, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated

from ..db import get_db
from ..main import QuickBot
from ..auth.telegram import check_telegram_auth
from ..auth.jwt import create_access_token

from logging import getLogger


logger = getLogger(__name__)
router = APIRouter()


@router.post("/webhook", name="telegram_webhook")
async def telegram_webhook(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
):
    logger.debug("Webhook request %s", await request.json())
    app: QuickBot = request.app

    if app.webhook_handler:
        return await app.webhook_handler(app=app, request=request)

    request_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if request_token != app.config.TELEGRAM_WEBHOOK_AUTH_KEY:
        logger.warning("Unauthorized request %s", request)
        return Response(status_code=403)
    try:
        update = Update(**await request.json())
    except Exception:
        logger.error("Invalid request", exc_info=True)
        return Response(status_code=400)

    try:
        await app.dp.feed_webhook_update(
            bot=app.bot,
            update=update,
            db_session=db_session,
            app=app,
            app_state=request.state,
        )
    except Exception:
        logger.error("Error processing update", exc_info=True)
        return Response(status_code=500)

    return Response(status_code=200)


@router.post("/auth")
async def telegram_login(request: Request, data: dict = Body(...)):
    if not check_telegram_auth(data, request.app.config.TELEGRAM_BOT_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid Telegram auth")
    payload = {
        "sub": str(data["id"]),
        "first_name": data.get("first_name"),
        "username": data.get("username"),
    }
    token = create_access_token(payload)
    return {"access_token": token, "token_type": "bearer"}


# async def feed_bot_update(
#     app: QBotApp,
#     update: Update,
#     app_state: State,
# ):
#     async with async_session() as db_session:
#         await app.dp.feed_webhook_update(
#             bot=app.bot,
#             update=update,
#             db_session=db_session,
#             app=app,
#             app_state=app_state,
#         )
