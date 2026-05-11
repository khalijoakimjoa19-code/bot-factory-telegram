# ============================================================
# webhook_server.py - Routes webhooks to correct bot instances
# ============================================================
import asyncio
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from telegram import Update
import database

logger = logging.getLogger(__name__)

_bot_applications = {}  # token -> Application
_bot_loop = None

def register_bot(token: str, application):
    """Register a bot application for webhook routing"""
    global _bot_loop
    _bot_applications[token] = application
    if not _bot_loop:
        _bot_loop = asyncio.get_event_loop()

app = Flask(__name__)

@app.route('/webhook/megapay', methods=['POST'])
def megapay_webhook():
    """Process MegaPay payment callbacks with bot_id routing"""
    data = request.get_json(force=True, silent=True) or {}
    logger.info(f"MegaPay webhook: {data}")
    
    try:
        response_code = data.get("ResponseCode")
        if str(response_code) != "0":
            return jsonify({"status": "ok"}), 200
            
        mpesa_ref = data.get("TransactionReceipt", "")
        reference = str(data.get("TransactionReference", ""))
        phone = str(data.get("Msisdn", ""))
        
        # Parse bot_id from reference: "bot_id:telegram_id"
        if ":" not in reference:
            logger.warning(f"Invalid reference format: {reference}")
            return jsonify({"status": "error", "message": "Invalid reference"}), 400
            
        bot_id_str, telegram_id_str = reference.split(":", 1)
        bot_id = int(bot_id_str)
        telegram_id = int(telegram_id_str)
        
        # Route to correct bot's database
        db = database.get_db()
        pending = asyncio.run_coroutine_threadsafe(
            db.get_pending_payment(bot_id, reference), _bot_loop
        ).result()
        
        if not pending:
            logger.warning(f"No pending payment for {reference}")
            return jsonify({"status": "ok"}), 200
            
        # Process payment in bot's context
        asyncio.run_coroutine_threadsafe(
            _handle_successful_payment(bot_id, telegram_id, phone, mpesa_ref, pending),
            _bot_loop
        ).result(timeout=30)
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Route Telegram updates to correct bot based on token in URL"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        token = data.get('token') or request.args.get('token')
        
        if not token:
            logger.warning("No token provided in webhook")
            return jsonify({"status": "error", "message": "No token"}), 400
            
        application = _bot_applications.get(token)
        if not application:
            logger.warning(f"No application for token {token[:10]}...")
            return jsonify({"status": "error", "message": "Unknown bot"}), 404
            
        update = Update.de_json(data, application.bot)
        asyncio.run_coroutine_threadsafe(
            application.process_update(update),
            _bot_loop
        ).result(timeout=30)
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running",
        "bots": len(_bot_applications),
        "uptime": str(datetime.now() - datetime.now())
    }), 200

async def _handle_successful_payment(bot_id, telegram_id, phone, mpesa_ref, pending):
    """Process successful payment for a bot instance"""
    from config import PLANS
    from datetime import datetime, timedelta
    
    db = database.get_db()
    bot_config = await db.get_bot(bot_id)
    if not bot_config:
        raise ValueError(f"Bot {bot_id} not found")
        
    plan = pending['plan']
    amount = pending['amount']
    plan_info = PLANS.get(plan, {})
    
    # Create subscription
    end_date = datetime.now() + timedelta(days=plan_info.get('days', 30))
    
    # Create invite link
    application = _bot_applications.get(bot_config['bot_token'])
    if not application:
        raise ValueError(f"Application for bot {bot_id} not found")
        
    invite = await application.bot.create_chat_invite_link(
        chat_id=bot_config['channel_id'],
        member_limit=1,
        name=f"{telegram_id}_{plan}"
    )
    
    # Add subscription and payment
    await db.add_subscription(
        bot_id, telegram_id, plan, amount, 
        end_date, invite.invite_link, mpesa_ref
    )
    await db.add_payment(bot_id, telegram_id, phone, amount, plan, mpesa_ref)
    await db.delete_pending_payment(bot_id, pending['checkout_request_id'])
    
    # Notify user
    try:
        user_msg = f"""
? *Payment Confirmed!*

?? Amount: KES {amount:,}
?? Plan: {plan_info.get('emoji', '')} {plan_info.get('label', plan)}
?? M-Pesa Ref: {mpesa_ref}
?? Expires: {end_date.strftime('%d %b %Y')}

?? *Your Private One-Time Invite Link:*
{invite.invite_link}

Welcome to the VIP Room! ??
"""
        await application.bot.send_message(
            chat_id=telegram_id, 
            text=user_msg,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {telegram_id}: {e}")
    
    # Notify admin
    try:
        admin_msg = f"""
?? *New Payment Received!*

?? User: {telegram_id}
?? Phone: {phone}
?? Amount: KES {amount:,}
?? Plan: {plan}
?? M-Pesa Ref: {mpesa_ref}
"""
        await application.bot.send_message(
            chat_id=bot_config['admin_id'] or telegram_id,
            text=admin_msg,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")
