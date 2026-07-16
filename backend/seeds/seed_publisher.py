"""
出版社数据初始化脚本
运行方式：python -m seeds.seed_publisher
"""

import asyncio
from sqlalchemy import select
from config.db_conf import AsyncSessionLocal
from models.publisher import Publisher
import models.book  # 解决 Publisher.books 关系的 forward reference


PUBLISHERS = [
    {"name": "人民邮电出版社", "description": "信息技术和通信领域的权威出版社"},
    {"name": "清华大学出版社", "description": "国内领先的计算机与工程教育出版机构"},
    {"name": "机械工业出版社", "description": "工程技术和科技类书籍的重要出版方"},
    {"name": "电子工业出版社", "description": "电子信息与计算机技术出版的领先者"},
    {"name": "中信出版社", "description": "经管和前沿科技领域的精品出版社"},
    {"name": "北京大学出版社", "description": "综合性高等教育教材出版机构"},
    {"name": "高等教育出版社", "description": "全国最大的高等教育教材出版社"},
    {"name": "O'Reilly Media", "description": "全球知名的技术书籍出版品牌"},
]


async def seed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Publisher))
        existing = result.scalars().all()
        if existing:
            print(f"publisher 表已有 {len(existing)} 条数据，跳过插入")
            return

        for item in PUBLISHERS:
            session.add(Publisher(**item))
        await session.commit()
        print(f"成功插入 {len(PUBLISHERS)} 条出版社数据")


if __name__ == "__main__":
    asyncio.run(seed())
