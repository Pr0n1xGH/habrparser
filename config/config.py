from dataclasses import dataclass
from environs import Env
from typing import List

@dataclass
class BotConfig:
    token: str
    channel_id: int
    admin_ids: List[int]
    mistral_api_key: str

@dataclass
class DatabaseConfig:
    url: str

@dataclass
class Config:
    bot: BotConfig
    db: DatabaseConfig

def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        bot=BotConfig(
            token=env.str("BOT_TOKEN"),
            channel_id=env.int("CHANNEL_ID"),
            admin_ids=list(map(int, env.list("ADMIN_IDS"))),
            mistral_api_key=env.str("MISTRAL_API_KEY")
        ),
        db=DatabaseConfig(
            url=env.str("DATABASE_URL", "sqlite+aiosqlite:///posts.db")
        )
    )