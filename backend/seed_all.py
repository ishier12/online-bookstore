"""
统一种子数据入口
运行方式：cd backend && uv run python seed_all.py

先导入所有模型（解决 SQLAlchemy relationship 的 forward reference 解析），
再按顺序执行各模块的种子数据。
"""

import asyncio
import random
from decimal import Decimal

# ====== 1. 导入所有模型（确保 SQLAlchemy 初始化前就注册好全部类） ======
import models.user
import models.publisher
import models.category
import models.book
import models.review
import models.cart          # 🔲 第二期
import models.address       # 🔲 第二期
import models.order         # 🔲 第二期
import models.payment       # 🔲 第二期
import models.user_favorite # 🔲 第二期

from config.db_conf import AsyncSessionLocal
from sqlalchemy import select, func
from models.publisher import Publisher
from models.category import Category
from models.book import Book


# ====== 2. 出版社数据 ======
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


# ====== 3. 分类数据（两级树） ======
CATEGORIES_TREE = [
    {
        "name": "编程语言",
        "children": [
            {"name": "Python"}, {"name": "Java"}, {"name": "JavaScript / TypeScript"},
            {"name": "Go"}, {"name": "Rust"}, {"name": "C / C++"},
        ],
    },
    {
        "name": "数据库",
        "children": [
            {"name": "MySQL"}, {"name": "Redis"}, {"name": "MongoDB"}, {"name": "PostgreSQL"},
        ],
    },
    {
        "name": "云计算与基础设施",
        "children": [
            {"name": "Docker"}, {"name": "Kubernetes"}, {"name": "微服务"}, {"name": "分布式系统"},
        ],
    },
    {
        "name": "人工智能",
        "children": [
            {"name": "机器学习"}, {"name": "深度学习"}, {"name": "自然语言处理"},
        ],
    },
    {
        "name": "软件工程",
        "children": [
            {"name": "设计模式"}, {"name": "敏捷开发"}, {"name": "系统设计"}, {"name": "版本控制 / Git"},
        ],
    },
]


# ====== 4. 书籍数据 ======
# price 使用 Decimal 而非 float，避免浮点精度问题（钱必须精确）
BOOKS_DATA = [
    {
        "book_name": "Python从入门到实践", "author": "张三", "price": Decimal("59.00"),
        "isbn": "978-7-115-00001-1", "cover_url": "https://example.com/covers/python-intro.jpg",
        "description": "适合零基础读者的 Python 入门教程，涵盖基础语法、面向对象、Web 开发和数据可视化。",
        "stock": 100, "publisher_name": "人民邮电出版社",
        "category_names": ["Python"],
    },
    {
        "book_name": "FastAPI实战", "author": "李四", "price": Decimal("79.00"),
        "isbn": "978-7-302-00002-2", "cover_url": "https://example.com/covers/fastapi.jpg",
        "description": "从零开始学习 FastAPI，构建高性能 RESTful API，涵盖认证、缓存、数据库和部署。",
        "stock": 50, "publisher_name": "清华大学出版社",
        "category_names": ["Python", "微服务"],
    },
    {
        "book_name": "深入理解Python", "author": "张三", "price": Decimal("89.00"),
        "isbn": "978-7-111-00003-3", "cover_url": "https://example.com/covers/deep-python.jpg",
        "description": "深入 Python 底层机制，涵盖元类、描述符、协程、GIL 等进阶主题。",
        "stock": 30, "publisher_name": "机械工业出版社",
        "category_names": ["Python"],
    },
    {
        "book_name": "数据结构与算法", "author": "王五", "price": Decimal("45.00"),
        "isbn": "978-7-302-00004-4", "cover_url": "https://example.com/covers/algo.jpg",
        "description": "经典数据结构与算法教材，用 Python 实现链表、树、图、排序和搜索。",
        "stock": 80, "publisher_name": "清华大学出版社",
        "category_names": ["Python"],
    },
    {
        "book_name": "MySQL从入门到精通", "author": "李四", "price": Decimal("69.00"),
        "isbn": "978-7-115-00005-5", "cover_url": "https://example.com/covers/mysql.jpg",
        "description": "全面讲解 MySQL 8.0，包含索引优化、事务、锁机制和主从复制。",
        "stock": 60, "publisher_name": "人民邮电出版社",
        "category_names": ["MySQL"],
    },
    {
        "book_name": "机器学习入门", "author": "赵六", "price": Decimal("99.00"),
        "isbn": "978-7-121-00006-6", "cover_url": "https://example.com/covers/ml-intro.jpg",
        "description": "机器学习基础教程，涵盖监督学习、无监督学习、特征工程和模型评估。",
        "stock": 40, "publisher_name": "电子工业出版社",
        "category_names": ["机器学习"],
    },
    {
        "book_name": "Docker容器实战", "author": "赵六", "price": Decimal("55.00"),
        "isbn": "978-7-121-00007-7", "cover_url": "https://example.com/covers/docker.jpg",
        "description": "Docker 从入门到生产实践，包含 Compose、Swarm、Kubernetes 入门。",
        "stock": 70, "publisher_name": "电子工业出版社",
        "category_names": ["Docker"],
    },
    {
        "book_name": "Redis深度历险", "author": "陈七", "price": Decimal("49.00"),
        "isbn": "978-7-111-00008-8", "cover_url": "https://example.com/covers/redis.jpg",
        "description": "深入 Redis 数据结构、持久化、哨兵和集群，从原理到实战全覆盖。",
        "stock": 55, "publisher_name": "机械工业出版社",
        "category_names": ["Redis"],
    },
    {
        "book_name": "Kubernetes权威指南", "author": "吴十", "price": Decimal("128.00"),
        "isbn": "978-7-121-00009-9", "cover_url": "https://example.com/covers/k8s.jpg",
        "description": "Kubernetes 生产级实践指南，涵盖 Pod、Service、Ingress、存储和监控。",
        "stock": 25, "publisher_name": "电子工业出版社",
        "category_names": ["Kubernetes", "分布式系统"],
    },
    {
        "book_name": "设计模式之美", "author": "刘八", "price": Decimal("75.00"),
        "isbn": "978-7-302-00010-10", "cover_url": "https://example.com/covers/patterns.jpg",
        "description": "深入 23 种经典设计模式，用 Python 和 Java 对照讲解，培养架构思维。",
        "stock": 45, "publisher_name": "清华大学出版社",
        "category_names": ["设计模式", "Python"],
    },
]


async def seed_all():
    async with AsyncSessionLocal() as session:
        # ── 出版社 ──
        existing = await session.execute(select(func.count(Publisher.id)))
        if existing.scalar() == 0:
            for item in PUBLISHERS:
                session.add(Publisher(**item))
            await session.flush()
            print(f"✅ 插入 {len(PUBLISHERS)} 条出版社数据")
        else:
            print(f"⏭️  出版社数据已存在，跳过")

        # ── 分类（两级树） ──
        existing = await session.execute(select(func.count(Category.id)))
        if existing.scalar() == 0:
            for top_data in CATEGORIES_TREE:
                children_data = list(top_data.pop("children", []))
                top = Category(name=top_data["name"])
                session.add(top)
                await session.flush()
                for child_data in children_data:
                    session.add(Category(name=child_data["name"], parent_id=top.id))
            await session.flush()
            print(f"✅ 插入分类数据")
        else:
            print(f"⏭️  分类数据已存在，跳过")

        # ── 书籍 ──
        existing = await session.execute(select(func.count(Book.id)))
        if existing.scalar() == 0:
            # 获取出版社和分类的 ID 映射
            pub_result = await session.execute(select(Publisher))
            publishers_map = {p.name: p for p in pub_result.scalars().all()}
            cat_result = await session.execute(select(Category))
            categories_map = {c.name: c for c in cat_result.scalars().all()}

            for item in BOOKS_DATA:
                category_names = item.pop("category_names", [])
                pub_name = item.pop("publisher_name", None)
                item["publisher_id"] = publishers_map[pub_name].id if pub_name in publishers_map else None
                book = Book(**item)
                for cname in category_names:
                    if cname in categories_map:
                        book.categories.append(categories_map[cname])
                session.add(book)

            await session.commit()
            print(f"✅ 插入 {len(BOOKS_DATA)} 条精选书籍")

            # ── 批量随机生成（目标 300 本，减去精选的 10 本 = 290 本）──
            TARGET_COUNT = 300
            to_generate = TARGET_COUNT - len(BOOKS_DATA)

            AUTHORS = ["张三", "李四", "王五", "赵六", "陈七", "刘八", "周九", "吴十",
                       "孙十一", "钱十二", "杨十三", "黄十四"]
            PREFIXES = [
                "深入理解", "实战", "从入门到精通", "高级编程", "核心原理",
                "经典教程", "设计与实现", "最佳实践", "从零开始学", "精通",
                "深入浅出", "权威指南", "快速上手", "企业级", "全栈",
            ]
            SUFFIXES = [
                "Python", "Java", "Go", "Rust", "JavaScript", "TypeScript",
                "Docker", "Kubernetes", "Redis", "MySQL", "MongoDB",
                "微服务", "分布式系统", "云计算", "人工智能",
                "Linux", "Nginx", "Elasticsearch", "Kafka", "RabbitMQ",
            ]
            all_publishers = list(publishers_map.values())
            all_categories = list(categories_map.values())

            batch_books = []
            for i in range(to_generate):
                book = Book(
                    book_name=f"{random.choice(PREFIXES)}{random.choice(SUFFIXES)}",
                    author=random.choice(AUTHORS),
                    price=Decimal(str(round(random.uniform(20, 150), 2))),
                    publisher_id=random.choice(all_publishers).id,
                    stock=random.randint(0, 200),
                )
                # 随机分配 1-3 个分类
                num_cats = random.randint(1, 3)
                selected_cats = random.sample(all_categories, min(num_cats, len(all_categories)))
                book.categories = selected_cats
                session.add(book)

            await session.commit()
            print(f"✅ 批量生成 {to_generate} 本书籍，总计 {TARGET_COUNT} 本")
        else:
            print(f"⏭️  书籍数据已存在，跳过")

        await session.commit()
        print("\n🎉 所有种子数据初始化完成")


if __name__ == "__main__":
    asyncio.run(seed_all())
