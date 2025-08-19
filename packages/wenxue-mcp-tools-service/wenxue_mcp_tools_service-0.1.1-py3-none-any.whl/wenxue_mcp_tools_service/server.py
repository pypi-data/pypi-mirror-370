from mcp.server.fastmcp import FastMCP
from .utils import download_pdf, validate_url
from .storage import upload_to_cloud  # 可选存储功能
import fitz
import base64
from io import BytesIO
from typing import Dict, List, Union, Optional
import os
from . import config
import pymysql
from mcp.server.fastmcp import FastMCP
from pymysql import MySQLError
import os
import pandas as pd
import requests
from io import BytesIO
from typing import List, Dict, Any
mcp = FastMCP("PDFToolsService")


def get_db_connection():
    """创建 MySQL 连接"""
    DB_CONFIG = {
        "host": os.getenv("mysql_host", ""),
        "port": int(os.getenv("mysql_port", "")),
        "user": os.getenv("mysql_user", ""),
        "password": os.getenv("mysql_password", ""),
        "database": os.getenv("mysql_database", "")
    }
    return pymysql.connect(**DB_CONFIG)


@mcp.tool(name="mysql_insert")
def mysql_insert(table_name: str, data: Dict[str, Any]) -> str:
    """
    向 MySQL 表插入一条数据
    :param table_name: 目标表名
    :param data: 数据字典（键为列名，值为数据）
    :return: 操作结果消息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(data.values()))
        conn.commit()
        return f"插入成功，影响行数: {cursor.rowcount}"
    except MySQLError as e:
        return f"数据库错误: {e}"
    finally:
        cursor.close()
        conn.close()

@mcp.tool(name="mysql_delete_table")
def mysql_delete_table(table_name: str) -> str:
    """
    删除 MySQL 数据表（慎用！）
    :param table_name: 目标表名
    :return: 操作结果消息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(sql)
        conn.commit()
        return f"表 {table_name} 已删除"
    except MySQLError as e:
        return f"数据库错误: {e}"
    finally:
        cursor.close()
        conn.close()

@mcp.tool(name="execute_sql")
def execute_sql(sql: str) -> List[Dict[str, Any]]:
    """
    执行 SQL 查询语句
    :param sql: SQL 语句
    :return: 查询结果（字典列表）
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except MySQLError as e:
        return [{"error": f"数据库错误: {e}"}]
    finally:
        cursor.close()
        conn.close()

@mcp.tool(name="excel_to_json")
def excel_to_json(url: str) -> List[Dict[str, Any]]:
    """
    从 URL 下载 Excel 文件并转换为 JSON 格式（List[Dict]）
    :param url: Excel 文件的 URL 地址
    :return: JSON 格式数据或错误信息
    """
    try:
        # 1. 从 URL 下载文件内容
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # 检查 HTTP 错误

        # 2. 验证是否为 Excel 文件
        content_type = response.headers.get('Content-Type', '').lower()
        if 'excel' not in content_type and 'spreadsheet' not in content_type and not url.lower().endswith(
                ('.xlsx', '.xls')):
            # 如果明确是二进制流但未提供扩展名，尝试自动识别
            if not url.lower().split('?')[0].endswith(('.xlsx', '.xls')):
                raise ValueError("URL 可能不是有效的 Excel 文件")

        # 3. 使用 BytesIO 在内存中处理文件
        excel_bytes = BytesIO(response.content)

        # 4. 读取 Excel 文件并转换为 JSON
        df = pd.read_excel(excel_bytes, engine='openpyxl')
        return df.to_dict(orient='records')

    except requests.RequestException as e:
        return [{"error": f"下载文件失败: {str(e)}"}]
    except Exception as e:
        return [{"error": f"文件处理失败: {str(e)}"}]

@mcp.tool()
def pdf_url_to_images(
        pdf_url: str,
        format: str = "png",
        zoom: float = 2.0,
        page_range: Optional[List[int]] = None,
        output_type: str = "base64"
) -> Dict[str, Union[List[Dict], str, int]]:
    """
    从PDF URL转换图片，返回Base64或存储URL

    参数:
    - pdf_url: PDF文件的公开URL
    - format: 图片格式 (png/jpg)，默认为png
    - zoom: 缩放比例 (0.5-5.0)，默认2.0
    - page_range: 指定转换的页码 (如 [0,2] 表示第1、3页)
    - output_type: 返回类型 - "base64"或"url"

    返回:
    {
        "page_count": 总页数,
        "pages": [
            {
                "page": 页码,
                "image": "base64字符串" 或 "图片URL",
                "format": 图片格式
            }
        ],
        "status": "success" 或 "error",
        "message": 状态描述
    }
    """
    # try:
    # 1. 验证URL安全性
    validate_url(pdf_url)

    # 2. 下载PDF
    pdf_content = download_pdf(pdf_url)

    # 3. 验证PDF大小
    max_size = config.PDF_MAX_SIZE_MB * 1024 * 1024
    if len(pdf_content) > max_size:
        raise ValueError(f"PDF超过大小限制 ({config.PDF_MAX_SIZE_MB}MB)")

    # 4. 打开PDF
    with fitz.open(stream=pdf_content, filetype="pdf") as doc:
        target_pages = page_range or list(range(len(doc)))
        results = []

        # 5. 逐页处理
        for pg_num in target_pages:
            page = doc.load_page(pg_num)
            pix = page.get_pixmap(
                matrix=fitz.Matrix(zoom, zoom)
            )
            img_data = pix.tobytes()

            # 6. 按输出类型处理结果
            if output_type == "base64":
                results.append({
                    "page": pg_num,
                    "image": base64.b64encode(img_data).decode("utf-8"),
                    "format": format
                })
            elif output_type == "url" and config.UPLOAD_ENABLED:
                image_url = upload_to_cloud(img_data, format)
                results.append({
                    "page": pg_num,
                    "url": image_url,
                    "format": format
                })
            else:
                results.append({
                    "page": pg_num,
                    "format": format,
                    "size_bytes": len(img_data)
                })

        return {
            "page_count": len(doc),
            "pages": results,
            "status": "success",
            "message": f"成功转换 {len(results)} 页"
        }

    # except Exception as e:
    #     return {
    #         "status": "error",
    #         "message": str(e),
    #         "pages": [],
    #         "page_count": 0
    #     }


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()