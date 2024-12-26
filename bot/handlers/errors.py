from aiogram import Router, F
from aiogram.types import ErrorEvent
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.errors()
async def error_handler(error: ErrorEvent):
    logger.error(f"Ошибка при обработке обновления: {error.exception}", exc_info=True) 