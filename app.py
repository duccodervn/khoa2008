# app.py
from flask import Flask, request, render_template, redirect
from config import SECRET_KEY, GOOGLE_DRIVE_LINK, TRUST_PROXY
from database import init_db, delete_expired
from key_manager import get_or_create_key, is_valid
import time

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Nếu đứng sau reverse proxy (Nginx/Cloudflare), có thể bật: app.config["APPLICATION_ROOT"]...
# Ở đây chỉ cần xử lý IP từ header khi TRUST_PROXY=True
def client_ip(req) -> str:
    if TRUST_PROXY:
        xff = req.headers.get("X-Forwarded-For", "")
        if xff:
            # lấy IP đầu tiên
            ip = xff.split(",")[0].strip()
            if ip:
                return ip
    # fallback
    return req.remote_addr or "0.0.0.0"

@app.before_first_request
def bootstrap():
    init_db()

@app.after_request
def _cleanup(resp):
    # dọn key hết hạn (nhẹ nhàng, không đồng bộ)
    try:
        delete_expired(int(time.time() * 1000))
    except Exception:
        pass
    return resp

@app.route("/")
def index():
    ip = client_ip(request)
    ua = request.headers.get("User-Agent", "")
    key, expires_at = get_or_create_key(ip, ua)
    return render_template("index.html", ip=ip, key=key, expires_at=expires_at)

@app.route("/access")
def access():
    key = request.args.get("key", "").strip()
    ip = client_ip(request)
    if not key:
        return render_template("error.html", message="Thiếu key truy cập"), 400
    if not is_valid(ip, key):
        return render_template("error.html", message="Key không hợp lệ hoặc đã hết hạn"), 403

    # Hợp lệ -> cho vào Drive (redirect)
    return redirect(GOOGLE_DRIVE_LINK, code=302)

if __name__ == "__main__":
    # Chạy local: python app.py -> http://localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
