#!/usr/bin/env python3
# Test to verify all modules can be imported

print("Testing Railway build compatibility...")
print("=" * 50)

passed = 0
failed = 0

try:
    import sys
    print(f"? Python {sys.version}")
    passed += 1
except Exception as e:
    print(f"? Python sys: {e}")
    failed += 1

try:
    from factory_database import FactoryDatabase
    print("? factory_database")
    passed += 1
except Exception as e:
    print(f"? factory_database: {e}")
    failed += 1

try:
    from factory_config import FACTORY_BOT_TOKEN, PLANS, POSTGRES_DSN
    print("? factory_config")
    passed += 1
except Exception as e:
    print(f"? factory_config: {e}")
    failed += 1

try:
    from factory_bot import FactoryBot, setup_factory_bot, run_factory_bot
    print("? factory_bot")
    passed += 1
except Exception as e:
    print(f"? factory_bot: {e}")
    failed += 1

print("=" * 50)
print(f"Results: {passed} passed, {failed} failed")

if failed == 0:
    print("? All imports successful - Railway build should work!")
    sys.exit(0)
else:
    print("? Import errors detected")
    sys.exit(1)