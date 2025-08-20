from aiogram.types import Update
from typing import Literal
from fastapi import Depends, Request, Response
from fastapi.datastructures import State
from faststream.rabbit.fastapi import ContextRepo
from faststream.rabbit import RabbitBroker
from logging import getLogger
from typing_extensions import Annotated
from quickbot import QuickBot
from quickbot.db import get_db
from sqlmodel.ext.asyncio.session import AsyncSession
from faststream.rabbit.fastapi import RabbitRouter

from .config import config
from .utils import override_route

logger = getLogger(__name__)

async def telegram_webhook(
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
        update = await request.json()
    except Exception:
        logger.error("Invalid request", exc_info=True)
        return Response(status_code=400)

    broker: RabbitBroker = request.state.broker

    await broker.publish(
        message=update,
        queue=f"{app.config.STACK_NAME}.telegram_updates",
    )

    return Response(status_code=200)


class FaststreamPlugin:
    def __init__(
        self,
    ) -> None:
        self.broker_router = None

    def register(self, app: QuickBot) -> None:
        self.broker_router = RabbitRouter(
            url=config.RABBITMQ_URL
        )
                
        @self.broker_router.subscriber(queue=f"{app.config.STACK_NAME}.telegram_updates", no_reply=True)
        async def telegram_updates_handler(
            message: dict,
            db_session: Annotated[AsyncSession, Depends(get_db)],
            context: ContextRepo,
        ):
            state = State(
                {
                    "broker": context.context["broker"],
                }
            )

            try:
                update = Update(**message)
                await app.dp.feed_webhook_update(
                    bot=app.bot,
                    update=update,
                    db_session=db_session,
                    app=app,
                    app_state=state,
                )
            except Exception:
                logger.error("Error processing update", exc_info=True)

        app.include_router(self.broker_router)

        override_route(app, name="telegram_webhook", new_endpoint=telegram_webhook)
            