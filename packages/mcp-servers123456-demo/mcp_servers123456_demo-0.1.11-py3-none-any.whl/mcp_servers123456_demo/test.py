import csv
import os
import pymysql
from pymysql import MySQLError
from typing import Any, Dict, List
import httpx
# 用于创建 MCP 服务
from mcp.server.fastmcp import FastMCP
# 初始化一个MCP服务实例，服务名称就是test_mcp_server，这将作为 MCP 客户端或大模型识别服务的标识
mcp = FastMCP("test_mcp_server")

DB_CONFIG = {
    "host": os.getenv("mysql_host", ""),
    "port": int(os.getenv("mysql_port", 3306)),
    "user": os.getenv("mysql_user", ""),
    "password": os.getenv("mysql_password", ""),
    "database": os.getenv("mysql_database", "")
}

def get_db_connection():
    """创建 MySQL 连接"""
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

@mcp.tool(description="Add two numbers.")
def add(aa: int, b: int) -> int:
    """
    Add two numbers and return the result.
    
    Args:
        aa: The first number to add
        b:  The sum of the two numbers
    
    Returns:
        str: The sum result
    """
    
    return aa + b

# 获取当前本地 ip 地址
@mcp.tool(  )
async def fetch_current_ip() -> str:
    """
        Fetch the current public IP address.
        No parameters needed.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://ipinfo.io/ip")
        return response.text


@mcp.tool()
def export_json_to_csv(json_data: List[Dict[str, str]]) -> str:
    """
    Export a list of {'question', 'answer'} dicts to a CSV file and upload it to a remote server.
    
    Args:
        json_data: A list of dictionaries, each containing 'question' and 'answer' keys.
    
    Returns:
        The URL of the uploaded CSV file or an error message if the upload fails.
    """
    csv_filename =  "output.csv"
    # 生成 CSV 文件
    with open(csv_filename, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["question", "answer"])
        writer.writeheader()
        for item in json_data:
            writer.writerow(item)
    
    # 上传文件
    url = "https://smartvision.dcclouds.com/api/v1/file/upload"
    headers = {"Authorization": "Bearer wf-T6CbvXStL2BooON5NcagcX1Q"}
    with open(csv_filename, "rb") as f:
        files = {"files": (csv_filename, f, "text/csv")}
        response = httpx.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        url = response.json()["data"][0]["url"]
        return url
    else:
        return f"CSV 文件已导出，但上传失败: {csv_filename}\n错误: {response.text}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()