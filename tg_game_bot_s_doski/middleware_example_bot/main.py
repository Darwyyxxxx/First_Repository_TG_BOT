import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.config import Config, load_config
from handlers.other import other_router
from handlers.user import user_router
from middlewares.inner import (
    FirstInnerMiddleware,
    SecondInnerMiddleware,
    ThirdInnerMiddleware,
)
from middlewares.outer import (
    FirstOuterMiddleware,
    SecondOuterMiddleware,
    ThirdOuterMiddleware,
)

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main() -> None:
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Задаём базовую конфигурацию логирования
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )
    # Инициализируем бот и диспетчер
    bot = Bot(token=config.bot.token)
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_router)
    dp.include_router(other_router)

    # Здесь будем регистрировать миддлвари
    dp.update.outer_middleware(FirstOuterMiddleware())
    user_router.callback_query.outer_middleware(SecondOuterMiddleware())
    other_router.message.outer_middleware(ThirdOuterMiddleware())
    user_router.message.middleware(FirstInnerMiddleware())
    user_router.callback_query.middleware(SecondInnerMiddleware())
    other_router.message.middleware(ThirdInnerMiddleware())

    # Запускаем polling
    await dp.start_polling(bot)


asyncio.run(main())