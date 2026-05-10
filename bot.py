# ============================================================
# bot.py - Complete Premium Bot (Copied from New folder)
# ============================================================
import logging
from datetime import datetime

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply,
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters,
)

import database
from mpesa import initiate_stk_push, is_valid_phone, format_phone
from config import (
    ADMIN_ID, ADMIN_USERNAME, SUPPORT_USERNAME, PLANS,
    WELCOME_MESSAGE, PAYMENT_PENDING_MESSAGE,
)

logger = logging.getLogger(__name__)

SELECT_PLAN = 0
ENTER_PHONE = 1
BROADCAST_MSG = 10
BROADCAST_TARGET = 11

def plan_keyboard():
    rows = []
    for key, plan in PLANS.items():
        rows.append([
            InlineKeyboardButton(
                f"{plan['emoji']} {plan['label']} — KES {plan['price']:,}",
                callback_data=f"plan_{key}",
            )
        ])
    rows.append([InlineKeyboardButton("?? Support", url=f"https://t.me/PREMIUMVVIPADMIN")])
    return InlineKeyboardMarkup(rows)

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Subscribe Now", callback_data="open_plans")],
        [InlineKeyboardButton("?? My Subscription", callback_data="my_sub")],
        [InlineKeyboardButton("?? Support", url="https://t.me/PREMIUMVVIPADMIN")],
    ])

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("?? Analytics", callback_data="admin_analytics")],
        [InlineKeyboardButton("?? Broadcast", callback_data="admin_broadcast_start")],
        [InlineKeyboardButton("?? Manual Reminders", callback_data="admin_remind_all")],
        [InlineKeyboardButton("?? View Subscribers", callback_data="admin_subscribers")],
        [InlineKeyboardButton("?? Refresh", callback_data="admin_refresh")],
    ])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.upsert_user(user.id, user.first_name, user.username or "")
    msg = WELCOME_MESSAGE.format(name=user.first_name)
    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    return SELECT_PLAN

async def open_plans(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "?? *Choose your subscription plan:*\n\n"
        "All plans give you instant access to the Premium VIP Channel.\n"
        "Payment is via M-Pesa STK Push.",
        parse_mode="Markdown",
        reply_markup=plan_keyboard(),
    )
    return SELECT_PLAN

async def my_subscription(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    sub = database.get_active_subscription(user_id)
    if not sub:
        await query.edit_message_text(
            "? You have no active subscription.\n\nTap /start to subscribe.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("?? Subscribe Now", callback_data="open_plans")
            ]]),
        )
        return SELECT_PLAN
    plan_info = PLANS.get(sub["plan"], {})
    end_dt = datetime.fromisoformat(str(sub["end_date"]))
    days_left = max(0, (end_dt - datetime.now()).days)
    await query.edit_message_text(
        f"? *Active Subscription*\n\n"
        f"?? Plan: {plan_info.get('emoji','')} {plan_info.get('label', sub['plan'])}\n"
        f"?? Expires: {end_dt.strftime('%d %b %Y at %H:%M')}\n"
        f"? Days Remaining: {days_left}\n\n"
        f"Enjoy the VIP Room! ??",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("?? Renew Now", callback_data="open_plans"),
            InlineKeyboardButton("?? Main Menu", callback_data="back_main"),
        ]]),
    )
    return SELECT_PLAN

async def back_main(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    msg = WELCOME_MESSAGE.format(name=user.first_name)
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    return SELECT_PLAN

async def handle_plan_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_key = query.data.replace("plan_", "")
    if plan_key not in PLANS:
        await query.answer("Unknown plan.", show_alert=True)
        return SELECT_PLAN
    plan_info = PLANS[plan_key]
    ctx.user_data["selected_plan"] = plan_key
    await query.edit_message_text(
        f"? You selected: *{plan_info['emoji']} {plan_info['label']} — KES {plan_info['price']:,}*\n\n"
        "?? Enter your *M-Pesa phone number* to receive the payment prompt:\n"
        "_(Example: 0712345678 or 254712345678)_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("?? Change Plan", callback_data="open_plans"),
            InlineKeyboardButton("? Cancel", callback_data="cancel_payment"),
        ]]),
    )
    return ENTER_PHONE

async def handle_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    phone_raw = update.message.text.strip()
    if not is_valid_phone(phone_raw):
        await update.message.reply_text(
            "?? Invalid phone number. Please enter a valid Kenyan M-Pesa number.\n"
            "Example: *0712345678*",
            parse_mode="Markdown",
        )
        return ENTER_PHONE
    phone = format_phone(phone_raw)
    plan_key = ctx.user_data.get("selected_plan")
    if not plan_key:
        await update.message.reply_text("Session expired. Please tap /start again.")
        return ConversationHandler.END
    plan_info = PLANS[plan_key]
    amount = plan_info["price"]
    user = update.effective_user
    database.update_user_phone(user.id, phone)
    waiting_msg = await update.message.reply_text(
        PAYMENT_PENDING_MESSAGE.format(amount=amount),
        parse_mode="Markdown",
    )
    result = await initiate_stk_push(phone, amount, plan_info["label"], telegram_id=user.id)
    if result["success"]:
        checkout_id = result["transaction_request_id"] or phone
        database.add_pending(user.id, phone, amount, plan_key, checkout_id)
        await waiting_msg.edit_text(
            f"?? *STK Push Sent!*\n\n"
            f"?? Amount: *KES {amount:,}*\n"
            f"?? To: {phone}\n\n"
            f"?? Enter your M-Pesa PIN on your phone.\n"
            f"Your invite link will arrive here automatically once payment is confirmed. ?\n\n"
            f"_If you don't receive the prompt, wait 30 seconds and tap the button below._",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("?? Resend STK Push", callback_data=f"resend_{plan_key}_{phone}"),
                InlineKeyboardButton("? Cancel", callback_data="cancel_payment"),
            ]]),
        )
    else:
        await waiting_msg.edit_text(
            f"? *STK Push Failed*\n\n"
            f"Reason: {result['message']}\n\n"
            "Please try again or contact @PREMIUMVVIPADMIN.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("?? Try Again", callback_data="open_plans"),
                InlineKeyboardButton("?? Support", url="https://t.me/PREMIUMVVIPADMIN"),
            ]]),
        )
    return SELECT_PLAN

async def handle_resend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Resending STK push…", show_alert=False)
    parts = query.data.split("_", 2)
    plan_key = parts[1] if len(parts) > 1 else None
    phone = parts[2] if len(parts) > 2 else None
    if not plan_key or not phone:
        await query.answer("Session expired. Please tap /start.", show_alert=True)
        return SELECT_PLAN
    plan_info = PLANS.get(plan_key, {})
    amount = plan_info.get("price", 0)
    result = await initiate_stk_push(phone, amount, plan_info.get("label", ""))
    if result["success"]:
        checkout_id = result["transaction_request_id"] or phone
        database.add_pending(update.effective_user.id, phone, amount, plan_key, checkout_id)
        await query.edit_message_text(
            f"?? New STK push sent to {phone}. Enter your PIN. ?",
            parse_mode="Markdown",
        )
    else:
        await query.answer(f"Failed: {result['message']}", show_alert=True)
    return SELECT_PLAN

async def cancel_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data.clear()
    await query.edit_message_text("? Payment cancelled. Tap /start to begin again.")
    return ConversationHandler.END

async def status_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sub = database.get_active_subscription(user_id)
    if not sub:
        await update.message.reply_text(
            "You have no active subscription.\n\nTap /start to subscribe.",
            reply_markup=main_menu_keyboard(),
        )
        return
    plan_info = PLANS.get(sub["plan"], {})
    end_dt = datetime.fromisoformat(str(sub["end_date"]))
    days_left = max(0, (end_dt - datetime.now()).days)
    await update.message.reply_text(
        f"? *Active Subscription*\n\n"
        f"?? Plan: {plan_info.get('emoji','')} {plan_info.get('label', sub['plan'])}\n"
        f"?? Expires: {end_dt.strftime('%d %b %Y at %H:%M')}\n"
        f"? Days Remaining: *{days_left}*",
        parse_mode="Markdown",
    )

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def admin_panel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("? Access denied.")
        return
    await update.message.reply_text(
        "??? *Admin Panel*\n\nWhat would you like to do?",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )

async def admin_analytics_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied.", show_alert=True)
        return
    await query.answer()
    stats = database.get_analytics()
    plan_lines = ""
    for pk, cnt in stats["plan_breakdown"].items():
        pi = PLANS.get(pk, {})
        plan_lines += f"  {pi.get('emoji','')} {pi.get('label', pk)}: {cnt}\n"
    recent_lines = ""
    for p in stats["recent_payments"][:5]:
        pi = PLANS.get(p["plan"], {})
        recent_lines += f"  • {p['first_name']} — KES {p['amount']:,} ({pi.get('label', p['plan'])}) — {p['mpesa_ref']}\n"
    text = (
        "?? *Bot Analytics*\n\n"
        f"?? Total Users: *{stats['total_users']}*\n"
        f"? Active Subs: *{stats['active_subs']}*\n"
        f"? Expired Subs: *{stats['expired_subs']}*\n\n"
        f"?? Total Revenue: *KES {stats['total_revenue']:,}*\n"
        f"?? This Month: *KES {stats['monthly_revenue']:,}*\n"
        f"?? Total Payments: *{stats['total_payments']}*\n\n"
        f"?? *Active by Plan:*\n{plan_lines or '  None'}\n"
        f"?? *Recent Payments:*\n{recent_lines or '  None'}"
    )
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("?? Refresh", callback_data="admin_analytics"),
            InlineKeyboardButton("?? Back", callback_data="admin_refresh"),
        ]]),
    )

async def admin_subscribers_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied.", show_alert=True)
        return
    await query.answer()
    subs = database.get_all_active_subscribers()
    if not subs:
        await query.edit_message_text(
            "No active subscribers at the moment.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("?? Back", callback_data="admin_refresh")
            ]]),
        )
        return
    lines = [f"?? *Active Subscribers ({len(subs)}):*\n"]
    for s in subs:
        uname = f"@{s['username']}" if s.get("username") else f"ID:{s['telegram_id']}"
        sub = database.get_active_subscription(s["telegram_id"])
        plan = PLANS.get(sub["plan"], {}).get("label", "?") if sub else "?"
        end_dt = datetime.fromisoformat(str(sub["end_date"])).strftime("%d %b") if sub else "?"
        lines.append(f"• {s['first_name']} ({uname}) — {plan} until {end_dt}")
    text = "\n".join(lines[:50])
    if len(subs) > 50:
        text += f"\n…and {len(subs)-50} more."
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("?? Back", callback_data="admin_refresh")
        ]]),
    )

async def admin_refresh_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("Access denied.", show_alert=True)
        return
    await query.answer()
    await query.edit_message_text(
        "??? *Admin Panel*\n\nWhat would you like to do?",
        parse_mode="Markdown", reply_markup=admin_keyboard(),
    )

def setup_bot(application: Application):
    user_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_PLAN: [
                CallbackQueryHandler(open_plans, pattern="^open_plans$"),
                CallbackQueryHandler(my_subscription, pattern="^my_sub$"),
                CallbackQueryHandler(back_main, pattern="^back_main$"),
                CallbackQueryHandler(handle_plan_selection, pattern="^plan_"),
                CallbackQueryHandler(handle_resend, pattern="^resend_"),
                CallbackQueryHandler(cancel_payment, pattern="^cancel_payment$"),
            ],
            ENTER_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone),
                CallbackQueryHandler(open_plans, pattern="^open_plans$"),
                CallbackQueryHandler(cancel_payment, pattern="^cancel_payment$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_user=True, per_chat=True, allow_reentry=True,
    )
    application.add_handler(user_conv)
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("status", status_cmd))
    application.add_handler(CallbackQueryHandler(admin_analytics_cb, pattern="^admin_analytics$"))
    application.add_handler(CallbackQueryHandler(admin_subscribers_cb, pattern="^admin_subscribers$"))
    application.add_handler(CallbackQueryHandler(admin_refresh_cb, pattern="^admin_refresh$"))
    logger.info("All handlers registered.")
