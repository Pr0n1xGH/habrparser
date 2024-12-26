import asyncio
import logging
from contextlib import AsyncExitStack

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import load_config
from database import Storage
from bot.utils.misc import setup_bot
from bot.handlers import admin, errors
from bot.middlewares import AdminMiddleware
from bot import ParserService, SummarizerService, StatsService

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Запуск бота...")
    config = load_config()
    
    storage = Storage(config.db.url)
    await storage.init_db()
    
    parser_service = ParserService()
    summarizer_service = SummarizerService(config.bot.mistral_api_key)
    
    bot = setup_bot(config.bot.token)
    await bot.delete_webhook(drop_pending_updates=True)
    
    dp = Dispatcher(storage=MemoryStorage())
    
    stats_service = StatsService(
        storage=storage,
        parser=parser_service,
        summarizer=summarizer_service,
        channel_id=config.bot.channel_id,
        bot=bot
    )
    
    logger.info(f"Админы: {config.bot.admin_ids}")
    
    dp.message.middleware(AdminMiddleware(config.bot.admin_ids))
    
    dp.include_router(admin.router)
    dp.include_router(errors.router)
    
    dp["stats_service"] = stats_service
    
    await stats_service.check_new_posts()
    
    scheduler.add_job(
        stats_service.check_new_posts,
        trigger="interval",
        minutes=5,
        misfire_grace_time=300
    )
    scheduler.start()
    
    async with AsyncExitStack() as stack:
        tasks = [asyncio.create_task(dp.start_polling(bot))]
        
        logger.info("Бот запущен и готов к работе!")
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")
        finally:
            logger.info("Завершение работы бота...")
            scheduler.shutdown()
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен!")
