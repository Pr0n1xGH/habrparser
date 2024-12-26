from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from datetime import datetime
from collections import Counter

from .models import Base, PostRecord, BotStats

class Storage:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.Session = sessionmaker(self.engine, class_=AsyncSession)

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with self.Session() as session:
            stats = await session.execute(select(BotStats))
            if not stats.scalar_one_or_none():
                session.add(BotStats(start_time=datetime.now()))
                await session.commit()

    async def is_post_exists(self, url: str) -> bool:
        async with self.Session() as session:
            stmt = select(PostRecord).where(PostRecord.url == url)
            result = await session.execute(stmt)
            post = result.scalar_one_or_none()
            return post is not None

    async def save_post(self, url: str, published_at: datetime, hubs: list[str] = None):
        async with self.Session() as session:
            new_post = PostRecord(
                url=url,
                published_at=published_at,
                hubs=','.join(hubs) if hubs else None
            )
            session.add(new_post)
            await session.commit()

    async def get_posts_count(self) -> int:
        async with self.Session() as session:
            result = await session.execute(select(func.count(PostRecord.id)))
            return result.scalar()

    async def get_last_posts(self, limit: int = 5) -> list[PostRecord]:
        async with self.Session() as session:
            result = await session.execute(
                select(PostRecord)
                .order_by(PostRecord.published_at.desc())
                .limit(limit)
            )
            return result.scalars().all()

    async def get_bot_stats(self) -> BotStats:
        async with self.Session() as session:
            result = await session.execute(select(BotStats))
            return result.scalar_one()

    async def update_stats(self, *, posts_processed: int = None, errors_count: int = None, last_check_time: datetime = None):
        async with self.Session() as session:
            stats = (await session.execute(select(BotStats))).scalar_one()
            
            if posts_processed is not None:
                stats.posts_processed = posts_processed
            if errors_count is not None:
                stats.errors_count = errors_count
            if last_check_time is not None:
                stats.last_check_time = last_check_time
            
            await session.commit()

    async def get_hubs_stats(self) -> dict[str, int]:
        async with self.Session() as session:
            result = await session.execute(select(PostRecord.hubs))
            all_hubs = result.scalars().all()
            
            hub_list = []
            for hubs_str in all_hubs:
                if hubs_str:
                    hub_list.extend(hubs_str.split(','))
            
            return dict(Counter(hub_list).most_common(10)) 