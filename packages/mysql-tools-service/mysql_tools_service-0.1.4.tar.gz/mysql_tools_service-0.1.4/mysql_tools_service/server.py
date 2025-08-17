import json

import pymysql
from mcp.server.fastmcp import FastMCP
from pymysql import MySQLError
import os
import pandas as pd
import requests
from io import BytesIO
from typing import List, Dict, Any

app = FastMCP("MySQL & Excel Tools")


# 数据库连接配置（需替换为实际值）
DB_CONFIG = {
    "host": os.getenv("mysql_host", ""),
    "port": int(os.getenv("mysql_port", "")),
    "user": os.getenv("mysql_user", ""),
    "password": os.getenv("mysql_password", ""),
    "database": os.getenv("mysql_database", "")
}

def get_db_connection():
    """创建 MySQL 连接"""
    return pymysql.connect(**DB_CONFIG)


@app.tool(name="mysql_insert")
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

@app.tool(name="mysql_delete_table")
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

@app.tool(name="execute_sql")
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

@app.tool(name="excel_to_json")
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

if __name__ == "__main__":
    app.run(transport="stdio")