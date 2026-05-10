# ============================================================
# mpesa.py - MegaPay STK Push integration
# ============================================================
import logging
import aiohttp
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

MEGAPAY_STK_URL = "https://megapay.co.ke/backend/v1/initiatestk"

def format_phone(phone: str) -> str:
    """Normalize Kenyan phone number to 254XXXXXXXXX"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        phone = phone[1:]
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    if not phone.startswith("254"):
        phone = "254" + phone
    return phone

def is_valid_phone(phone: str) -> bool:
    """Validate Kenyan phone number"""
    formatted = format_phone(phone)
    return (
        formatted.startswith("254") 
        and len(formatted) == 12 
        and formatted[3:].isdigit()
    )

async def initiate_stk_push(
    phone: str, amount: int, plan_label: str, 
    telegram_id: int, bot_id: int, api_key: str, email: str
) -> Dict:
    """Send STK push to MegaPay"""
    formatted_phone = format_phone(phone)
    
    # Reference format: bot_id:telegram_id for routing
    reference = f"{bot_id}:{telegram_id}"
    
    payload = {
        "api_key": api_key,
        "email": email,
        "amount": str(amount),
        "msisdn": formatted_phone,
        "reference": reference,
    }
    
    headers = {"Content-Type": "application/json"}
    
    logger.info(f"MegaPay STK ? phone={formatted_phone}, amount={amount}, ref={reference}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                MEGAPAY_STK_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                data = await resp.json(content_type=None)
                logger.info(f"MegaPay response ({resp.status}): {data}")
                
                success = str(data.get("success", "")) == "200"
                transaction_id = data.get("transaction_request_id", "")
                message = data.get("massage") or data.get("message") or (
                    "STK push sent successfully" if success else "STK push failed"
                )
                
                return {
                    "success": success,
                    "transaction_request_id": transaction_id,
                    "message": message,
                    "reference": reference,
                    "raw": data,
                }
                
    except aiohttp.ClientConnectorError as e:
        logger.error(f"MegaPay connection error: {e}")
        return {
            "success": False,
            "transaction_request_id": "",
            "message": "Could not reach payment server. Please try again.",
        }
    except Exception as e:
        logger.error(f"MegaPay unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "transaction_request_id": "",
            "message": f"Payment error: {str(e)}",
        }
