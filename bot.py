# ============================================================
# bot.py - Complete Premium Bot
# ============================================================
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes, filters
import database
from mpesa import initiate_stk_push, is_valid_phone, format_phone
from config import ADMIN_ID, PLANS, WELCOME_MESSAGE, PAYMENT_PENDING_MESSAGE

logger = logging.getLogger(__name__)

SELECT_PLAN = 0
ENTER_PHONE = 1

def plan_keyboard():
    rows = []
    for key, plan in PLANS.items():
        rows.append([InlineKeyboardButton(f"{plan['emoji']} {plan['label']} - KES {plan['price']:,}", callback_data=f"plan_{key}")])
    rows.append([InlineKeyboardButton("Support", url=f"https://t.me/PREMIUMVVIPADMIN")])
    return InlineKeyboardMarkup(rows)

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Subscribe Now", callback_data="open_plans")],
        [InlineKeyboardButton("My Subscription", callback_data="my_sub")],
        [InlineKeyboardButton("Support", url="https://t.me/PREMIUMVVIPADMIN")],
    ])

