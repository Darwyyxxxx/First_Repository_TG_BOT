import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class FirstInnerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        logger.debug(
            "Вошли в миддлварь %s, тип события %s",
            __class__.__name__,
            event.__class__.__name__,
        )

        result = await handler(event, data)

        logger.debug("Выходим из миддлвари  %s", __class__.__name__)

        return result


class SecondInnerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        logger.debug(
            "Вошли в миддлварь %s, тип события %s",
            __class__.__name__,
            event.__class__.__name__,
        )

        # result = await handler(event, data)

        logger.debug("Выходим из миддлвари  %s", __class__.__name__)

        return


class ThirdInnerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        logger.debug(
            "Вошли в миддлварь %s, тип события %s",
            __class__.__name__,
            event.__class__.__name__,
        )

        result = await handler(event, data)

        logger.debug("Выходим из миддлвари  %s", __class__.__name__)

        return result