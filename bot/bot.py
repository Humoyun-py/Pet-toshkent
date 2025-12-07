import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start_router, pets_router, clinics_router, donation_router, admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    
    # Check token
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("❌ BOT_TOKEN not configured! Please set your bot token in config.py")
        logger.info("Get your token from @BotFather on Telegram")
        return
    
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register routers
    dp.include_router(start_router)
    dp.include_router(pets_router)
    dp.include_router(clinics_router)
    dp.include_router(donation_router)
    dp.include_router(admin_router)
    
    # Start polling
    logger.info("🚀 Bot is starting...")
    logger.info("🐾 Pet Tashkent Bot is running!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
