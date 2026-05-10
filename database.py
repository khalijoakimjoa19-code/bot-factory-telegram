# ============================================================
# database.py - Simplified database wrapper for bot instances
# ============================================================
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

def _conn():
    con = sqlite3.connect("bot.db", check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    return con

def init_db():
    """Initialize SQLite for single bot mode"""
    con = _conn()
    c = con.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            plan TEXT NOT NULL,
            amount INTEGER NOT NULL,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP NOT NULL,
            active INTEGER DEFAULT 1,
            reminded INTEGER DEFAULT 0,
            invite_link TEXT,
            payment_ref TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS pending_payments (
            checkout_request_id TEXT PRIMARY KEY,
            telegram_id INTEGER,
            phone TEXT,
            amount INTEGER,
            plan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    con.commit()
    con.close()
    logger.info("Database initialized")

def upsert_user(telegram_id: int, first_name: str, username: str):
    con = _conn()
    con.execute("""
        INSERT OR REPLACE INTO users (telegram_id, first_name, username)
        VALUES (?, ?, ?)
    """, (telegram_id, first_name or "User", username or ""))
    con.commit()
    con.close()

def update_user_phone(telegram_id: int, phone: str):
    con = _conn()
    con.execute("UPDATE users SET phone=? WHERE telegram_id=?", (phone, telegram_id))
    con.commit()
    con.close()

def get_user(telegram_id: int) -> Optional[Dict]:
    con = _conn()
    row = con.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
    con.close()
    return dict(row) if row else None

def add_pending(telegram_id: int, phone: str, amount: int, plan: str, checkout_request_id: str):
    con = _conn()
    con.execute("""
        INSERT OR REPLACE INTO pending_payments
        (telegram_id, phone, amount, plan, checkout_request_id)
        VALUES (?, ?, ?, ?, ?)
    """, (telegram_id, phone, amount, plan, checkout_request_id))
    con.commit()
    con.close()

def get_pending(checkout_request_id: str) -> Optional[Dict]:
    con = _conn()
    row = con.execute("SELECT * FROM pending_payments WHERE checkout_request_id=?",
                      (checkout_request_id,)).fetchone()
    con.close()
    return dict(row) if row else None

def delete_pending(checkout_request_id: str):
    con = _conn()
    con.execute("DELETE FROM pending_payments WHERE checkout_request_id=?",
                (checkout_request_id,))
    con.commit()
    con.close()

def add_subscription(telegram_id: int, plan: str, amount: int, end_date: datetime,
                   invite_link: str, payment_ref: str):
    con = _conn()
    con.execute("UPDATE subscriptions SET active=0 WHERE telegram_id=? AND active=1",
                (telegram_id,))
    con.execute("""
        INSERT INTO subscriptions (telegram_id, plan, amount, start_date, end_date,
                                   active, invite_link, payment_ref)
        VALUES (?, ?, ?, ?, ?, 1, ?, ?)
    """, (telegram_id, plan, amount, datetime.now(), end_date, invite_link, payment_ref))
    con.commit()
    con.close()

def get_active_subscription(telegram_id: int) -> Optional[Dict]:
    con = _conn()
    row = con.execute("""
        SELECT * FROM subscriptions 
        WHERE telegram_id=? AND active=1
    """, (telegram_id,)).fetchone()
    con.close()
    return dict(row) if row else None

def get_all_active_subscribers() -> List[Dict]:
    con = _conn()
    rows = con.execute("""
        SELECT DISTINCT u.telegram_id, u.first_name, u.username
        FROM users u
        JOIN subscriptions s ON u.telegram_id = s.telegram_id
        WHERE s.active = 1
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]

def get_analytics() -> Dict:
    con = _conn()
    total_users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    active_subs = con.execute("SELECT COUNT(*) FROM subscriptions WHERE active=1").fetchone()[0]
    expired_subs = con.execute("SELECT COUNT(*) FROM subscriptions WHERE active=0").fetchone()[0]
    total_revenue = con.execute("SELECT COALESCE(SUM(amount),0) FROM subscriptions").fetchone()[0]
    total_payments = con.execute("SELECT COUNT(*) FROM subscriptions").fetchone()[0]
    plan_rows = con.execute("SELECT plan, COUNT(*) as cnt FROM subscriptions WHERE active=1 GROUP BY plan").fetchall()
    plan_breakdown = {r["plan"]: r["cnt"] for r in plan_rows}
    recent = con.execute("""
        SELECT s.*, u.first_name FROM subscriptions s
        JOIN users u ON s.telegram_id = u.telegram_id
        ORDER BY s.created_at DESC LIMIT 5
    """).fetchall()
    recent_payments = [dict(r) for r in recent]
    con.close()
    return {
        "total_users": total_users,
        "active_subs": active_subs,
        "expired_subs": expired_subs,
        "total_revenue": total_revenue,
        "total_payments": total_payments,
        "plan_breakdown": plan_breakdown,
        "recent_payments": recent_payments
    }
