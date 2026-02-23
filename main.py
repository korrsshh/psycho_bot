import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
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

async def on_startup(bot: Bot):
    """Вызывается при запуске: устанавливаем webhook"""
    # URL твоего сервиса на Render
    base_url = os.getenv("BASE_URL", "https://твой-сервис.onrender.com")
    webhook_path = f"/webhook/{bot.token}"
    webhook_url = f"{base_url}{webhook_path}"
    
    # Удаляем старый webhook (на всякий случай)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Устанавливаем новый
    await bot.set_webhook(
        webhook_url,
        allowed_updates=dp.resolve_used_update_types()
    )
    logger.info(f"✅ Webhook установлен: {webhook_url}")

async def main():
    config = Config()
    
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    global dp  # Делаем dp глобальным для setup_application
    dp = Dispatcher()
    
    # Инициализация БД
    db = Database()
    await db.init_db()
    logger.info("✅ База данных инициализирована")
    
    # Подключение роутеров
    dp.include_router(user.router)
    dp.include_router(admin.router)
    
    # Регистрация хука на запуск
    dp.startup.register(on_startup)
    
    # Настройка aiohttp-сервера
    app = web.Application()
    
    # Создаём обработчик запросов от Telegram
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.WEBHOOK_SECRET  # Опционально: защита от фейковых запросов
    )
    webhook_requests_handler.register(app, path=f"/webhook/{bot.token}")
    
    # Health check для Render
    async def health_handler(request):
        return web.Response(text="OK", status=200)
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    
    # Подключаем aiogram к aiohttp
    setup_application(app, dp, bot=bot)
    
    # Запуск сервера
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    
    logger.info(f"🚀 Бот запущен на порту {port}")
    logger.info(f"👤 Админ ID: {config.ADMIN_ID}")
    
    # Держим процесс запущенным
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise