import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiohttp import web  # ← Добавляем для HTTP-сервера
from config import Config
from database import Database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Импортируем роутеры
from handlers import user, admin

# 🌐 Минимальный HTTP-сервер для Render
async def handle_health(request):
    """Отвечает на запросы Render, чтобы он не убивал процесс"""
    return web.Response(text="OK", status=200)

async def start_dummy_server(port: int):
    """Запускает простой сервер на нужном порту"""
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info(f"🌐 Dummy server running on port {port}")

async def main():
    config = Config()
    
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    db = Database()
    
    # Инициализация БД
    await db.init_db()
    logger.info("✅ База данных инициализирована")
    
    # Подключение роутеров
    dp.include_router(user.router)
    dp.include_router(admin.router)
    
    # 🌐 Запускаем dummy-сервер для Render
    # Render задаёт порт через переменную PORT, по умолчанию 10000
    port = int(os.getenv("PORT", 10000))
    asyncio.create_task(start_dummy_server(port))
    
    # Запуск polling
    bot_info = await bot.me()
    username_display = bot_info.username or "без username"
    logger.info(f"✅ Бот запущен (@{username_display})")
    logger.info(f"👤 Админ ID: {config.ADMIN_ID}")
    logger.info(f"👩‍⚕️ Психолог: {config.PSYCHOLOGIST_USERNAME}")
    logger.info(f"📢 Канал для подписки: {config.CHANNEL_ID}")
    
    # 🚀 Запускаем polling (основной процесс)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise