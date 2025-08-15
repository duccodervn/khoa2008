# key_manager.py
import secrets
import time
from typing import Tuple, Optional
from database import fetch_by_ip, upsert
from config import KEY_TTL_SECONDS

def _now_ms() -> int:
    return int(time.time() * 1000)

def _generate_key() -> str:
    # URL-safe random key
    return secrets.token_urlsafe(24)

def get_or_create_key(ip: str, user_agent: str) -> Tuple[str, int]:
    """
    Trả về (key, expires_at_ms) cho IP hiện tại.
    - Nếu key còn hạn: trả key cũ.
    - Nếu hết hạn/chưa có: tạo key mới, hạn = now + 24h.
    """
    now = _now_ms()
    row = fetch_by_ip(ip)
    if row:
        _, key, _, created_at, expires_at = row
        if expires_at > now:
            return key, expires_at
    # Tạo mới
    key = _generate_key()
    created_at = now
    expires_at = now + (KEY_TTL_SECONDS * 1000)
    upsert(ip=ip, key=key, user_agent=(user_agent or "")[:255], created_at=created_at, expires_at=expires_at)
    return key, expires_at

def is_valid(ip: str, key: str) -> bool:
    now = _now_ms()
    row = fetch_by_ip(ip)
    if not row:
        return False
    _, saved_key, _, _, expires_at = row
    return (saved_key == key) and (expires_at > now)
