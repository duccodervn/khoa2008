# config.py

# Chuỗi bí mật của Flask (đổi thành chuỗi dài & khó đoán trong triển khai thật)
SECRET_KEY = "change-this-secret-key-please-32+chars"

# Link Google Drive sẽ được truy cập khi key hợp lệ
GOOGLE_DRIVE_LINK = "https://drive.google.com/drive/folders/1xN7z9En0-bkuGDuYYbVsta3iYhVCqjE_?usp=drive_link"

# Thời gian sống của key: 24 giờ (tính bằng giây)
KEY_TTL_SECONDS = 24 * 60 * 60  # 86400

# Nếu deploy sau reverse proxy (Nginx/Cloudflare), bật True để đọc X-Forwarded-For
TRUST_PROXY = True
