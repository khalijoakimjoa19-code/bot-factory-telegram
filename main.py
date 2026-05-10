# ============================================================
# main.py - Entry point for bot factory
# ============================================================
import asyncio
import logging
import sys

from telegram.ext import Application

from factory_config import FACTORY_BOT_TOKEN, PLANS
from factory_bot import setup_factory_bot, run_factory_bot
from factory_database import FactoryDatabase
from factory_config import POSTGRES_DSN

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def main():
    """Start the bot factory"""
    try:
        # Initialize PostgreSQL database
        logger.info("Initializing PostgreSQL database...")
        db = FactoryDatabase(POSTGRES_DSN)
        await db.connect()
        
        # Create factory application
        application = Application.builder().token(FACTORY_BOT_TOKEN).build()
        
        # Setup factory bot handlers
        logger.info("Setting up factory bot...")
        setup_factory_bot(application, db)
        
        # Start the bot
        logger.info("Starting factory bot...")
        await run_factory_bot(application, db)
        
    except Exception as e:
        logger.error(f"Failed to start factory: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
