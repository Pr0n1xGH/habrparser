from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.filters import CommandObject

class AdminMiddleware(BaseMiddleware):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids
        
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        command = data.get("command")
        if not isinstance(command, CommandObject):
            return await handler(event, data)
        
        if event.from_user.id not in self.admin_ids:
            await event.answer("⛔️ У вас нет прав для использования этой команды")
            return
            
        return await handler(event, data) 