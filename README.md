# Habr News Bot 🤖 | Бот для новостей с Хабра

[English](#english) | [Русский](#russian)

## English

A Telegram bot that automatically collects interesting articles from Habr.com and posts them to a Telegram channel.

### Features
- 🤖 Automatically finds and fetches new posts from Habr
- 🧠 Uses AI to create concise summaries of long articles
- 📱 Posts news directly to your Telegram channel
- 🖼 Handles images from articles
- 📊 Provides beautiful hub statistics

### Bot Commands
- 📊 `/status` - Check bot status:
  - Uptime
  - Processed posts count
  - Most popular hubs (with graph)
  - Recently found posts
  - General statistics
- 🔄 `/force_check` - Force check for new posts immediately

### Technical Stack
- Python 3.11+
- aiogram 3
- SQLite (with SQLAlchemy)
- Checks for new posts every 5 minutes
- Protected commands through middleware

### Setup Instructions
1. Install Python 3.11 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` file with the following variables:
   ```
   BOT_TOKEN=your_bot_token_from_@BotFather
   CHANNEL_ID=your_channel_id
   ADMIN_IDS=admin_id1,admin_id2
   MISTRAL_API_KEY=your_mistral_ai_key
   DATABASE_URL=sqlite+aiosqlite:///posts.db
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

### Requirements
- Channel must be public
- Bot must be an admin in the channel

## Русский

Телеграм-бот, который автоматически собирает интересные статьи с Хабра и публикует их в телеграм-канале.

### Возможности
- 🤖 Автоматически находит и собирает новые посты с Хабра
- 🧠 Использует AI для создания кратких пересказов длинных статей
- 📱 Публикует новости прямо в телеграм-канал
- 🖼 Обрабатывает изображения из статей
- 📊 Предоставляет красивую статистику по хабам

### Команды бота
- 📊 `/status` - Проверить статус бота:
  - Время работы
  - Количество обработанных постов
  - Самые популярные хабы (с графиком)
  - Недавно найденные посты
  - Общая статистика
- 🔄 `/force_check` - Принудительно проверить новые посты

### Технический стек
- Python 3.11+
- aiogram 3
- SQLite (через SQLAlchemy)
- Проверка новых постов каждые 5 минут
- Защищенные команды через middleware

### Инструкция по установке
1. Установите Python 3.11 или выше
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создайте файл `.env` со следующими переменными:
   ```
   BOT_TOKEN=токен_от_@BotFather
   CHANNEL_ID=id_вашего_канала
   ADMIN_IDS=id_админа1,id_админа2
   MISTRAL_API_KEY=ключ_от_mistral_ai
   DATABASE_URL=sqlite+aiosqlite:///posts.db
   ```
4. Запустите бота:
   ```bash
   python bot.py
   ```

### Требования
- Канал должен быть публичным
- Бот должен быть администратором канала

---

### Contact | Контакты
Telegram: [@nob0dy_tg](https://t.me/nob0dy_tg)

### License | Лицензия
GPL-3.0 license
