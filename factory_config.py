# ============================================================
# factory_config.py - Factory configuration management
# ============================================================
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# Factory Core Settings
# ============================================================
FACTORY_BOT_TOKEN = os.getenv("FACTORY_BOT_TOKEN")
if not FACTORY_BOT_TOKEN:
    raise ValueError("FACTORY_BOT_TOKEN environment variable is required")

FACTORY_ADMIN_ID = int(os.getenv("FACTORY_ADMIN_ID", "8584329987"))

# ============================================================
# PostgreSQL Database
# ============================================================
POSTGRES_DSN = os.getenv("POSTGRES_DSN")
if not POSTGRES_DSN:
    POSTGRES_USER = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or "postgres"
    POSTGRES_PASSWORD = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or "postgres"
    POSTGRES_HOST = os.getenv("PGHOST") or os.getenv("POSTGRES_HOST") or "localhost"
    POSTGRES_PORT = os.getenv("PGPORT") or os.getenv("POSTGRES_PORT") or "5432"
    POSTGRES_DB = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or "botfactory"
    POSTGRES_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ============================================================
# MegaPay Configuration (Shared for all bots)
# ============================================================
MEGAPAY_API_KEY = os.getenv("MEGAPAY_API_KEY")
MEGAPAY_EMAIL = os.getenv("MEGAPAY_EMAIL")

if not MEGAPAY_API_KEY or not MEGAPAY_EMAIL:
    raise ValueError("MEGAPAY_API_KEY and MEGAPAY_EMAIL environment variables are required")

# ============================================================
# Server Configuration
# ============================================================
WEBHOOK_PORT = int(os.getenv("PORT", "5000"))
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")

if RAILWAY_PUBLIC_DOMAIN:
    WEBHOOK_URL = f"https://{RAILWAY_PUBLIC_DOMAIN}/webhook/factory"
else:
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# ============================================================
# Shared Subscription Plans (All bots use same plans)
# ============================================================
PLANS = {
    "daily": {"label": "Daily", "price": 250, "days": 1, "emoji": "?"},
    "weekly": {"label": "Weekly", "price": 1000, "days": 7, "emoji": "??"},
    "monthly": {"label": "Monthly", "price": 3500, "days": 30, "emoji": "???"},
    "quarterly": {"label": "3 Months", "price": 10000, "days": 90, "emoji": "??"},
    "yearly": {"label": "Yearly", "price": 35000, "days": 365, "emoji": "??"},
}

# ============================================================
# Channel Configuration (All bots share the same channel)
# ============================================================
SHARED_CHANNEL_ID = int(os.getenv("SHARED_CHANNEL_ID", "-1003701835008"))

# ============================================================
# Reminder Settings
# ============================================================
REMINDER_DAYS_BEFORE = 2

# ============================================================
# Messages (Shared templates)
# ============================================================
WELCOME_MESSAGE = (
    "Welcome, {name}! ??\n\n"
    "?? *Premium Channel Subscription Assistant Bot (18+)*\n\n"
    "Choose a package, pay via M-Pesa, and you'll receive a "
    "private one-time invite link to the VIP Room.\n\n"
    "Need help? Tap ?? Support or message @PREMIUMVVIPADMIN."
)

PAYMENT_PENDING_MESSAGE = (
    "?? *STK Push Sent!*\n\n"
    "Check your phone — enter M-Pesa PIN to pay *KES {amount}*.\n\n"
    "? Waiting for confirmation… (up to 2 minutes)\n"
    "Once paid, your invite link will appear here automatically."
)

PAYMENT_SUCCESS_MESSAGE = (
    "? *Payment Confirmed!*\n\n"
    "?? Amount: KES {amount:,}\n"
    "?? Plan: {emoji} {plan}\n"
    "?? M-Pesa Ref: {mpesa_ref}\n"
    "?? Expires: {end_date}\n\n"
    "?? *Your Private One-Time Invite Link:*\n"
    "{invite_link}\n\n"
    "?? This link is *one-time use only*. Do not share it.\n"
    "Welcome to the VIP Room! ??"
)

EXPIRY_REMINDER_MESSAGE = (
    "? Hey {name}!\n\n"
    "Your *{plan}* subscription expires in *{days} day(s)* "
    "(on {date}).\n\n"
    "Renew now to keep enjoying exclusive content! ??\n\n"
    "Tap the button below to renew:"
)

RESUBSCRIBE_MESSAGE = (
    "?? Hey {name},\n\n"
    "We noticed your subscription expired ??\n\n"
    "Don't miss out on exclusive content!\n"
    "Tap below to re-subscribe:"
)
