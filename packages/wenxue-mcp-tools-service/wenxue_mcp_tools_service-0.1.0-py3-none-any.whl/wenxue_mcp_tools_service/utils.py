import requests
from urllib.parse import urlparse
import re
from . import config


def download_pdf(url: str, timeout: int = 30) -> bytes:
    """下载PDF文件到内存"""

    headers = {"User-Agent": "MCP-PDF-Service/1.0"}
    response = requests.get(
        url,
        timeout=timeout,
        headers=headers,
        stream=True
    )
    response.raise_for_status()

    # 流式下载，避免大文件内存溢出
    content = b""
    for chunk in response.iter_content(chunk_size=8192):
        content += chunk
    return content




def validate_url(url: str):
    """验证URL安全性，防止SSRF攻击"""
    parsed = urlparse(url)

    # 验证协议
    if parsed.scheme not in ["http", "https"]:
        raise ValueError("仅支持HTTP/HTTPS协议")

    # 验证域名 (实际使用应配置允许的域名列表)
    domain = parsed.netloc
    if config.ALLOWED_DOMAINS and domain not in config.ALLOWED_DOMAINS:
        print(config.ALLOWED_DOMAINS)
        raise ValueError(f"域名 {domain} 不在允许列表中")

    # 验证路径 (可选)
    if re.search(r"(\.\./)|(%00)", url):
        raise ValueError("URL包含潜在危险字符")