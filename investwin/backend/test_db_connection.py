#!/usr/bin/env python3
"""
测试 asyncpg 数据库连接
"""
import asyncio
import asyncpg
import os

async def test_connection():
    connection_string = "postgresql://huihui:investwin123@localhost:5432/investwin"

    try:
        print("尝试连接数据库...")
        conn = await asyncpg.connect(connection_string)
        print("✅ 数据库连接成功!")

        print("测试查询 stocks 表...")
        rows = await conn.fetch("SELECT * FROM stocks ORDER BY symbol")
        print(f"✅ 查询成功! 找到 {len(rows)} 条记录")

        for row in rows:
            print(f"  {row['symbol']}: {row['name']} - ${row.get('market_cap', 'N/A')}")

        await conn.close()
        print("✅ 连接已关闭")

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

    return True

if __name__ == "__main__":
    asyncio.run(test_connection())