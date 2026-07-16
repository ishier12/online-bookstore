"""
分类数据初始化脚本（两级层级：顶级分类 → 子分类）
运行方式：python -m seeds.seed_category

注意：需要先执行 seed_publisher.py 确保 publisher 表有数据
"""

import asyncio
from sqlalchemy import select
from config.db_conf import AsyncSessionLocal
from models.category import Category
import models.book  # 解决 Category.books 关系的 forward reference


CATEGORIES_TREE = [
    {
        "name": "编程语言",
        "children": [
            {"name": "Python"},
            {"name": "Java"},
            {"name": "JavaScript / TypeScript"},
            {"name": "Go"},
            {"name": "Rust"},
            {"name": "C / C++"},
        ],
    },
    {
        "name": "数据库",
        "children": [
            {"name": "MySQL"},
            {"name": "Redis"},
            {"name": "MongoDB"},
            {"name": "PostgreSQL"},
        ],
    },
    {
        "name": "云计算与基础设施",
        "children": [
            {"name": "Docker"},
            {"name": "Kubernetes"},
            {"name": "微服务"},
            {"name": "分布式系统"},
        ],
    },
    {
        "name": "人工智能",
        "children": [
            {"name": "机器学习"},
            {"name": "深度学习"},
            {"name": "自然语言处理"},
        ],
    },
    {
        "name": "软件工程",
        "children": [
            {"name": "设计模式"},
            {"name": "敏捷开发"},
            {"name": "系统设计"},
            {"name": "版本控制 / Git"},
        ],
    },
]


async def seed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Category))
        existing = result.scalars().all()
        if existing:
            print(f"category 表已有 {len(existing)} 条数据，跳过插入")
            return

        for top_data in CATEGORIES_TREE:
            # 创建顶级分类
            children_data = top_data.pop("children", [])
            top = Category(name=top_data["name"])
            session.add(top)
            await session.flush()  # 获取 top.id

            # 创建子分类
            for child_data in children_data:
                child = Category(name=child_data["name"], parent_id=top.id)
                session.add(child)

        await session.commit()

        # 汇总输出
        result = await session.execute(
            select(Category).where(Category.parent_id.is_(None))
        )
        tops = result.scalars().all()
        total = 0
        for t in tops:
            child_count = len(t.children)
            total += 1 + child_count
            print(f"  📂 {t.name} ({child_count} 个子分类)")
        print(f"成功插入 {total} 条分类数据")


if __name__ == "__main__":
    asyncio.run(seed())
