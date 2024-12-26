from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, LinkPreviewOptions
from datetime import datetime
import time

from bot.services.stats import StatsService

router = Router()

@router.message(Command("status"))
async def status_handler(message: Message, stats_service: StatsService):
    stats = await stats_service.get_bot_stats()
    uptime = datetime.now() - stats.start_time
    posts_count = await stats_service.get_posts_count()
    last_posts = await stats_service.get_last_posts(5)
    hubs_stats = await stats_service.get_hubs_stats()
    
    stats_text = "\n".join(
        f"• {hub}: {count} постов"
        for hub, count in hubs_stats.items()
    )
    
    chart = await stats_service.generate_hubs_chart(hubs_stats)
    
    await message.answer_photo(
        photo=chart,
        caption=f"📊 <b>Статус бота:</b>\n\n"
        f"⏱ Аптайм: {uptime.days}д {uptime.seconds//3600}ч {(uptime.seconds//60)%60}м\n"
        f"📈 Обработано постов: {stats.posts_processed}\n"
        f"💾 Всего постов в БД: {posts_count}\n"
        f"❌ Ошибок: {stats.errors_count}\n"
        f"🔄 Последняя проверка: {stats.last_check_time.strftime('%H:%M:%S') if stats.last_check_time else 'нет'}\n"
        f"📡 ID канала: {message.bot.id}\n\n"
        f"📝 <b>Популярные хабы:</b>\n{stats_text}\n\n"
        f"📝 Последние посты:\n" +
        "\n".join(f"• {post.url} ({post.published_at.strftime('%d.%m %H:%M')})" 
                 for post in last_posts),
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )

@router.message(Command("force_check"))
async def force_check_handler(message: Message, stats_service: StatsService):
    status_msg = await message.answer("🔄 Запускаю проверку новых постов...")
    start_time = time.time()
    
    await stats_service.check_new_posts()
    
    check_time = time.time() - start_time
    stats = await stats_service.get_bot_stats()
    await status_msg.edit_text(
        f"✅ Проверка завершена за {check_time:.2f}с\n\n"
        f"📊 Статистика последней проверки:\n"
        f"• Найдено постов: {stats.posts_processed}\n"
        f"• Время обработки: {check_time:.2f}с\n"
        f"• Последний пост: {stats.last_check_time.strftime('%H:%M:%S') if stats.last_check_time else 'нет'}"
    ) 