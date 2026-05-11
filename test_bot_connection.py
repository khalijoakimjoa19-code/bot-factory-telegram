# Quick connectivity test
import asyncio
from telegram import Bot
import os

async def test_bot():
    token = os.getenv('FACTORY_BOT_TOKEN', '8537889816:AAGffqSQwJL1YlzKvE_IRtO1r09Km0O_Mlc')
    try:
        bot = Bot(token)
        me = await bot.get_me()
        print(f"✓ Bot connected successfully!")
        print(f"✓ Username: @{me.username}")
        print(f"✓ ID: {me.id}")
        return True
    except Exception as e:
        print(f"✗ Bot connection failed: {e}")
        return False

if __name__ == "__main__":
    try:
        asyncio.run(test_bot())
    except Exception as e:
        print(f"✗ Test failed: {e}")
