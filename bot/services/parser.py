import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class HabrPost:
    title: str
    url: str
    author: str
    published_at: datetime
    preview_text: str
    images: list[str] = None
    full_text: str | None = None
    hubs: list[str] = None

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.hubs is None:
            self.hubs = []

class ParserService:
    BASE_URL = "https://habr.com/ru/news/"

    async def get_full_post_content(self, session: aiohttp.ClientSession, url: str) -> tuple[str, list[str], list[str]]:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            
            article_body = soup.select_one('div.article-formatted-body')
            full_text = article_body.get_text(strip=True) if article_body else ""
            
            hubs_list = soup.select('.tm-separated-list__list .tm-hubs-list__link span')
            hubs = [hub.text.strip() for hub in hubs_list]  
            
            images = []
            if article_body:
                for img in article_body.select('img[data-src]'):
                    if 'data-src' in img.attrs:
                        images.append(img['data-src'])
            
            return full_text, hubs, images

    def parse_datetime(self, datetime_str: str) -> datetime:
        try:
            return datetime.fromisoformat(datetime_str)
        except ValueError:
            try:
                if datetime_str.endswith('Z'):
                    datetime_str = datetime_str[:-1] + '+00:00'
                return datetime.fromisoformat(datetime_str)
            except ValueError as e:
                logger.error(f"Не удалось распарсить дату '{datetime_str}': {e}")
                return datetime.now()

    async def get_latest_post(self) -> HabrPost | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                article = soup.select_one('div.tm-articles-list article.tm-articles-list__item')
                
                if article:
                    preview_text = article.select_one('.article-formatted-body').get_text(strip=True)
                    url = f"https://habr.com{article.select_one('h2.tm-title a')['href']}"
                    
                    full_text, hubs, images = await self.get_full_post_content(session, url)
                    
                    time_element = article.select_one('time')
                    datetime_str = time_element['datetime'] if time_element else None
                    
                    if not datetime_str:
                        logger.error("Не найдена дата публикации")
                        published_at = datetime.now()
                    else:
                        published_at = self.parse_datetime(datetime_str)
                    
                    return HabrPost(
                        title=article.select_one('h2.tm-title span').text.strip(),
                        url=url,
                        author=article.select_one('a.tm-user-info__username').text.strip(),
                        published_at=published_at,
                        preview_text=preview_text,
                        images=images,
                        full_text=full_text,
                        hubs=hubs
                    )
                return None