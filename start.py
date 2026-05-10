# Start script for Railway
# Environment variables loaded from Railway Config

import logging
from factory_config import POSTGRES_DSN, FACTORY_BOT_TOKEN
from factory_database import FactoryDatabase
from factory_bot import setup_factory_bot, run_factory_bot
from telegram.ext import Application

logging.basicConfig(level=logging.INFO)

async def main():
    db = FactoryDatabase(POSTGRES_DSN)
    await db.connect()
    app = Application.builder().token(FACTORY_BOT_TOKEN).build()
    setup_factory_bot(app, db)
    await run_factory_bot(app, db)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
