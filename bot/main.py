"""Точка входа бота NOTLOVE.ME

Запуск:
    python main.py          — long-polling (разработка)
    python main.py webhook  — webhook-режим (продакшн)
"""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PORT
from handlers import router
from scheduler import send_daily_reminders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def scheduler_loop(bot: Bot) -> None:
    """Планировщик ежедневных напоминаний (20:00 МСК)."""
    import datetime as dt

    MSK = dt.timezone(dt.timedelta(hours=3))

    while True:
        now = dt.datetime.now(MSK)
        # Следующее 20:00 МСК
        target = now.replace(hour=20, minute=0, second=0, microsecond=0)
        if now >= target:
            target += dt.timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        logger.info(f"Следующие напоминания через {wait_seconds / 3600:.1f} ч")
        await asyncio.sleep(wait_seconds)

        try:
            await send_daily_reminders(bot)
        except Exception as e:
            logger.error(f"Ошибка в планировщике: {e}")


async def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не задан. Укажите токен в .env файле.")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN, default={"parse_mode": ParseMode.MARKDOWN})
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    use_webhook = len(sys.argv) > 1 and sys.argv[1] == "webhook"

    if use_webhook and WEBHOOK_URL:
        from aiohttp import web
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

        await bot.set_webhook(WEBHOOK_URL)
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        setup_application(app, dp, bot=bot)

        # Запускаем планировщик в фоне
        asyncio.create_task(scheduler_loop(bot))

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
        await site.start()
        logger.info(f"Webhook-сервер запущен на порту {WEBHOOK_PORT}")
        await asyncio.Event().wait()
    else:
        # Long-polling
        logger.info("Запуск в режиме long-polling")

        # Планировщик в фоне
        asyncio.create_task(scheduler_loop(bot))

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
