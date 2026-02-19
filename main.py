import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # ← КЛЮЧЕВОЙ ИМПОРТ
from config import Config
from database import Database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Импортируем роутеры ПОСЛЕ настройки логирования
from handlers import user, admin

async def main():
    config = Config()
    
    # ✅ ПРАВИЛЬНАЯ УСТАНОВКА ГЛОБАЛЬНОГО PARSE_MODE:
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
    
    # Запуск поллинга
    bot_info = await bot.me()
    username_display = bot_info.username or "без username"
    logger.info(f"✅ Бот запущен (@{username_display})")
    logger.info(f"👤 Админ ID: {config.ADMIN_ID}")
    logger.info(f"👩‍⚕️ Психолог: {config.PSYCHOLOGIST_USERNAME}")
    logger.info(f"📢 Канал для подписки: {config.CHANNEL_ID}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise