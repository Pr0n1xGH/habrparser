from datetime import datetime
import time
import matplotlib.pyplot as plt
import tempfile
import os
import asyncio
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
import logging
from typing import Dict

from bot.services.parser import ParserService, HabrPost
from bot.services.summarizer import SummarizerService
from database.storage import Storage

logger = logging.getLogger(__name__)

class StatsService:
    def __init__(
        self, 
        storage: Storage, 
        parser: ParserService,
        summarizer: SummarizerService,
        channel_id: int,
        bot: Bot = None
    ):
        self.storage = storage
        self.parser = parser
        self.summarizer = summarizer
        self.channel_id = channel_id
        self.bot = bot

    def set_bot(self, bot: Bot):
        self.bot = bot

    async def get_bot_stats(self):
        return await self.storage.get_bot_stats()

    async def get_posts_count(self) -> int:
        return await self.storage.get_posts_count()

    async def get_last_posts(self, limit: int = 5):
        return await self.storage.get_last_posts(limit)

    async def get_hubs_stats(self) -> Dict[str, int]:
        return await self.storage.get_hubs_stats()

    async def check_new_posts(self):
        try:
            if not self.bot:
                from bot.utils.misc import bot
                self.bot = bot

            latest_post = await self.parser.get_latest_post()
            
            if latest_post and not await self.storage.is_post_exists(latest_post.url):
                logger.info(f"Найден новый пост: {latest_post.title}")
                await self.process_post(latest_post)
                stats = await self.get_bot_stats()
                await self.storage.update_stats(
                    posts_processed=stats.posts_processed + 1,
                    last_check_time=datetime.now()
                )
            else:
                logger.info("Новых постов не найдено")
                await self.storage.update_stats(last_check_time=datetime.now())
        except Exception as e:
            logger.error(f"Ошибка при проверке постов: {e}")
            stats = await self.get_bot_stats()
            await self.storage.update_stats(
                errors_count=stats.errors_count + 1,
                last_check_time=datetime.now()
            )

    async def process_post(self, post: HabrPost):
        summary = await self.summarizer.summarize(post.full_text)
        
        max_length = 1000
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."

        message_text = f"{summary}\n\n"

        try:
            if post.images:
                media_group = [
                    InputMediaPhoto(
                        media=post.images[0],
                        caption=message_text
                    )
                ]
                
                media_group.extend([
                    InputMediaPhoto(media=image_url)
                    for image_url in post.images[1:]
                ])
                
                await self.bot.send_media_group(
                    chat_id=self.channel_id,
                    media=media_group
                )
            else:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message_text,
                )

            await self.storage.save_post(post.url, post.published_at, post.hubs)
        except Exception as e:
            logger.error(f"Ошибка при отправке поста: {e}")
            stats = await self.get_bot_stats()
            await self.storage.update_stats(errors_count=stats.errors_count + 1)

    async def generate_hubs_chart(self, hubs_stats: dict[str, int]) -> FSInputFile:
        plt.figure(figsize=(10, 6))
        plt.bar(hubs_stats.keys(), hubs_stats.values(), color='skyblue')
        plt.xticks(rotation=45, ha='right')
        plt.title('Популярные хабы')
        plt.tight_layout()
        
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_path = os.path.join(temp_dir, f'hubs_stats_{int(time.time())}.png')
        plt.savefig(temp_path, format='png')
        
        plt.close()
        
        temp_file = FSInputFile(temp_path)
        
        async def cleanup():
            await asyncio.sleep(5)
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        asyncio.create_task(cleanup())
        
        return temp_file