# ============================================================
# config.py - Configuration for individual bot instances
# ============================================================
from typing import Dict, Any

# This config is loaded per bot instance from factory database
# Default plans (can be overridden per bot via config JSON)
PLANS = {
    "daily": {"label": "Daily", "price": 250, "days": 1, "emoji": "?"},
    "weekly": {"label": "Weekly", "price": 1000, "days": 7, "emoji": "??"},
    "monthly": {"label": "Monthly", "price": 3500, "days": 30, "emoji": "???"},
    "quarterly": {"label": "3 Months", "price": 10000, "days": 90, "emoji": "??"},
    "yearly": {"label": "Yearly", "price": 35000, "days": 365, "emoji": "??"},
}

WELCOME_MESSAGE = (
    "Welcome, {name}! ??\n\n"
    "?? *Premium Channel Subscription Assistant Bot (18+)*\n\n"
    "Choose a package, pay via M-Pesa, and you'll receive a "
    "private one-time invite link to the VIP Room.\n\n"
    "Need help? Tap ?? Support."
)

PAYMENT_PENDING_MESSAGE = (
    "?? *STK Push Sent!*\n\n"
    "Check your phone — enter M-Pesa PIN to pay *KES {amount}*.\n\n"
    "? Waiting for confirmation… (up to 2 minutes)\n"
    "Once paid, your invite link will appear here automatically."
)

EXPIRY_REMINDER_MESSAGE = (
    "? Hey {name}!\n\n"
    "Your *{plan}* subscription expires in *{days} day(s)* "
    "(on {date}).\n\n"
    "Renew now to keep enjoying exclusive content! ??"
)

RESUBSCRIBE_MESSAGE = (
    "?? Hey {name},\n\n"
    "We noticed your subscription expired ??\n\n"
    "Don't miss out on exclusive content!\n"
    "Tap below to re-subscribe:"
)
