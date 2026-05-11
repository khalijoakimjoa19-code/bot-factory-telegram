# Update main.py for Railway compatibility
import asyncio
import logging
import sys
from telegram.ext import Application
from factory_config import FACTORY_BOT_TOKEN, PLANS
from factory_bot import setup_factory_bot, run_factory_bot
from factory_database import FactoryDatabase
from factory_config import POSTGRES_DSN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def main():
    """Start the bot factory"""
    try:
        logger.info("Initializing PostgreSQL database...")
        db = FactoryDatabase(POSTGRES_DSN)
        await db.connect()
        
        logger.info("Setting up factory bot...")
        application = Application.builder().token(FACTORY_BOT_TOKEN).build()
        setup_factory_bot(application, db)
        
        await run_factory_bot(application, db)
        
    except Exception as e:
        logger.error(f"Failed to start factory: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
