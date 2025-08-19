
from mcp.server.fastmcp import FastMCP
import mysql.connector
import re
from typing import List, Dict, Any

# 配置日志
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 酒店链接模板
# HOTEL_PAGE_TEMPLATE = "https://yourbooking.com/hotel?id={hotel_id}"
# HOTEL_APP_LINK = "appInternalJump://hotel/{hotel_id}"  # 只是一个标记，不是真实网页
HOTEL_LINK_TEMPLATE = '<a href="javascript:void(0)" data-hotel-id="{hotel_id}" style="color:#007AFF;text-decoration:underline">查看详情</a>'


# 数据库配置（请修改为你的实际配置）
DB_CONFIG = {
    "host": "rm-bp1un2iccg5796p08to.mysql.rds.aliyuncs.com",
    "port": 3306,
    "user": "lohas",
    "password": "Lohas123",
    "database": "hotel_bidder",
}

# 创建 MCP 服务器
mcp = FastMCP("HotelMCP")


# =======================
# 数据库查询函数
# =======================
def query_hotels_by_name(name: str) -> List[Dict[str, Any]]:
    """根据酒店名称模糊查询未过期的酒店"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT HotelID, Name, Name_CN, CityName, CityName_CN, StarRating, Address 
            FROM dao_lv_data 
            WHERE (Name LIKE %s OR Name_CN LIKE %s) 
              AND expired = 0
            LIMIT 10
        """
        pattern = f"%{name}%"
        cursor.execute(query, (pattern, pattern))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"数据库查询失败: {e}")
        return []


# =======================
# MCP Tool: 搜索酒店（返回 dict 或 str）
# =======================
@mcp.tool()
def search_hotels(hotel_name: str) -> Dict[str, Any]:
    """
    Search for hotels by name (English or Chinese).
    Returns a dictionary with content and is_error flag.
    """
    if not hotel_name or len(hotel_name.strip()) == 0:
        return {
            "content": "Error: hotel_name is required.",
            "is_error": True
        }

    hotels = query_hotels_by_name(hotel_name.strip())

    if not hotels:
        return {
            "content": f"No hotels found matching '{hotel_name}'.",
            "is_error": False
        }

    result_lines = [f"Found {len(hotels)} hotel(s) matching '{hotel_name}':\n"]
    for h in hotels:
        name = h["Name_CN"] or h["Name"]
        city = h["CityName_CN"] or h["CityName"]
        star = h["StarRating"] or "N/A"
        address = h["Address"] or h.get("Address_CN", "Unknown")
        link = HOTEL_LINK_TEMPLATE.format(hotel_id=h["HotelID"])

        line = (
            f"- **{name}** ({city}) ⭐{star} {link}\n"
            f"  地址: {address}"
        )
        result_lines.append(line)

    return {
        "content": "\n\n".join(result_lines),
        "is_error": False
    }



def main() -> None:
    mcp.run(transport="stdio")
