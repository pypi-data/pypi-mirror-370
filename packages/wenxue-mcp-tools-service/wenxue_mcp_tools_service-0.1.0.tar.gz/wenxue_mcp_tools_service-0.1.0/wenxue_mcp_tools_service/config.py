import os

# PDF处理配置
PDF_MAX_SIZE_MB = int(os.getenv("PDF_MAX_SIZE_MB", 50))  # 最大50MB

# URL安全配置
ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "")  # 示例: "example.com,arxiv.org"

# 云存储配置 (可选)
UPLOAD_ENABLED = os.getenv("UPLOAD_ENABLED", "false").lower() == "true"
QCLOUD_SECRET_ID = os.getenv("QCLOUD_SECRET_ID", "")
QCLOUD_SECRET_KEY = os.getenv("QCLOUD_SECRET_KEY", "")
QCLOUD_REGION = os.getenv("QCLOUD_REGION", "")
QCLOUD_TOKEN = os.getenv("QCLOUD_TOKEN", "")
QCLOUD_SCHEME = os.getenv("QCLOUD_SCHEME", "")
QCLOUD_BUCKET_NAME = os.getenv("QCLOUD_BUCKET_NAME", "")
QCLOUD_APP_ID = os.getenv("QCLOUD_APP_ID", "")
API_KEYS = os.getenv("API_KEYS", "default-key").split(",")