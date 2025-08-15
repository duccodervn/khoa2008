# database.py
import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "keys.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            ip TEXT PRIMARY KEY,
            key TEXT NOT NULL,
            user_agent TEXT,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_expires ON keys(expires_at)")
    conn.commit()
    conn.close()

def fetch_by_ip(ip: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT ip, key, user_agent, created_at, expires_at FROM keys WHERE ip = ?", (ip,))
    row = cur.fetchone()
    conn.close()
    return row

def upsert(ip: str, key: str, user_agent: str, created_at: int, expires_at: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO keys (ip, key, user_agent, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(ip) DO UPDATE SET
            key=excluded.key,
            user_agent=excluded.user_agent,
            created_at=excluded.created_at,
            expires_at=excluded.expires_at
    """, (ip, key, user_agent, created_at, expires_at))
    conn.commit()
    conn.close()

def delete_expired(now_ms: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM keys WHERE expires_at <= ?", (now_ms,))
    deleted = cur.rowcount if cur.rowcount is not None else 0
    conn.commit()
    conn.close()
    return deleted
