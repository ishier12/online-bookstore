"""
统一种子数据入口
运行方式：cd backend && uv run python seed_all.py

先导入所有模型（解决 SQLAlchemy relationship 的 forward reference 解析），
再按顺序执行：出版社 → 分类 → 精选书籍 → 批量生成
"""

import asyncio
import random
from decimal import Decimal

# ====== 1. 导入所有模型 ======
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


# ====== 2. 出版社 ======
PUBLISHERS = [
    {"name": "人民文学出版社", "description": "中国最大的文学出版机构，成立于1951年"},
    {"name": "商务印书馆", "description": "中国历史最悠久的现代出版机构，以学术和工具书著称"},
    {"name": "三联书店", "description": "生活·读书·新知三联书店，人文社科精品出版品牌"},
    {"name": "中信出版社", "description": "经管和前沿科技领域的精品出版社"},
    {"name": "上海译文出版社", "description": "外国文学与社科著作翻译出版的领军者"},
    {"name": "人民邮电出版社", "description": "信息技术和通信领域的权威出版社"},
    {"name": "机械工业出版社", "description": "工程技术和科技类书籍的重要出版方"},
    {"name": "电子工业出版社", "description": "电子信息与计算机技术出版的领先者"},
    {"name": "北京大学出版社", "description": "综合性高等教育教材出版机构"},
    {"name": "清华大学出版社", "description": "国内领先的计算机与工程教育出版机构"},
]


# ====== 3. 分类（两级树，覆盖多个领域） ======
CATEGORIES_TREE = [
    {
        "name": "文学小说",
        "children": [
            {"name": "中国文学"}, {"name": "外国文学"},
            {"name": "科幻奇幻"}, {"name": "悬疑推理"},
            {"name": "世界名著"},
        ],
    },
    {
        "name": "人文社科",
        "children": [
            {"name": "历史"}, {"name": "哲学"}, {"name": "心理学"},
            {"name": "社会学"}, {"name": "政治法律"},
        ],
    },
    {
        "name": "经济管理",
        "children": [
            {"name": "商业经管"}, {"name": "投资理财"}, {"name": "市场营销"},
            {"name": "经济学"},
        ],
    },
    {
        "name": "科学技术",
        "children": [
            {"name": "编程语言"}, {"name": "数据库与存储"}, {"name": "云计算与架构"},
            {"name": "人工智能"}, {"name": "科普"},
        ],
    },
    {
        "name": "生活休闲",
        "children": [
            {"name": "美食烹饪"}, {"name": "旅游地理"}, {"name": "健康养生"},
            {"name": "家居园艺"},
        ],
    },
    {
        "name": "艺术设计",
        "children": [
            {"name": "绘画书法"}, {"name": "摄影"}, {"name": "建筑"},
            {"name": "音乐"},
        ],
    },
]


# ====== 4. 精选书籍（真实书名和作者，覆盖各分类） ======
BOOKS_DATA = [
    # ═══════════ 文学小说：中国文学 ═══════════
    {"book_name": "活着", "author": "余华", "price": Decimal("45.00"),
     "isbn": "978-7-5302-1109-0", "description": "讲述了一个人一生的故事，展现了中国社会几十年的变迁。",
     "stock": 200, "publisher_name": "人民文学出版社", "category_names": ["中国文学"]},
    {"book_name": "围城", "author": "钱锺书", "price": Decimal("36.00"),
     "isbn": "978-7-02-002475-9", "description": "中国现代文学经典，以幽默讽刺的笔触描绘知识分子的困境。",
     "stock": 150, "publisher_name": "人民文学出版社", "category_names": ["中国文学"]},
    {"book_name": "三体", "author": "刘慈欣", "price": Decimal("93.00"),
     "isbn": "978-7-5366-9293-0", "description": "雨果奖获奖作品，中国科幻文学的里程碑。",
     "stock": 300, "publisher_name": "人民文学出版社", "category_names": ["中国文学", "科幻奇幻"]},
    {"book_name": "平凡的世界", "author": "路遥", "price": Decimal("108.00"),
     "isbn": "978-7-5302-1026-0", "description": "茅盾文学奖作品，全景式展现中国当代城乡社会生活。",
     "stock": 180, "publisher_name": "人民文学出版社", "category_names": ["中国文学"]},
    {"book_name": "红楼梦", "author": "曹雪芹", "price": Decimal("59.70"),
     "isbn": "978-7-02-000220-7", "description": "中国古典四大名著之首，封建社会的百科全书。",
     "stock": 250, "publisher_name": "人民文学出版社", "category_names": ["中国文学", "世界名著"]},
    {"book_name": "骆驼祥子", "author": "老舍", "price": Decimal("28.00"),
     "isbn": "978-7-02-001234-5", "description": "老舍代表作，讲述北京车夫祥子的悲惨命运。",
     "stock": 170, "publisher_name": "人民文学出版社", "category_names": ["中国文学"]},
    {"book_name": "呐喊", "author": "鲁迅", "price": Decimal("22.00"),
     "isbn": "978-7-02-009987-6", "description": "鲁迅短篇小说集，中国现代文学的开山之作。",
     "stock": 200, "publisher_name": "人民文学出版社", "category_names": ["中国文学", "世界名著"]},
    {"book_name": "边城", "author": "沈从文", "price": Decimal("24.00"),
     "isbn": "978-7-02-010452-7", "description": "沈从文代表作，湘西小镇上纯美而忧伤的爱情故事。",
     "stock": 140, "publisher_name": "人民文学出版社", "category_names": ["中国文学"]},
    {"book_name": "黄金时代", "author": "王小波", "price": Decimal("35.00"),
     "isbn": "978-7-5302-0890-8", "description": "王小波成名作，以黑色幽默书写知青时代的荒诞与自由。",
     "stock": 160, "publisher_name": "人民文学出版社", "category_names": ["中国文学"]},

    # ═══════════ 文学小说：外国文学 ═══════════
    {"book_name": "百年孤独", "author": "加西亚·马尔克斯", "price": Decimal("55.00"),
     "isbn": "978-7-5442-5399-4", "description": "魔幻现实主义代表作，讲述布恩迪亚家族七代人的故事。",
     "stock": 120, "publisher_name": "上海译文出版社", "category_names": ["外国文学", "世界名著"]},
    {"book_name": "挪威的森林", "author": "村上春树", "price": Decimal("36.00"),
     "isbn": "978-7-5327-4292-9", "description": "村上春树最具代表性的青春恋爱小说。",
     "stock": 160, "publisher_name": "上海译文出版社", "category_names": ["外国文学"]},
    {"book_name": "1984", "author": "乔治·奥威尔", "price": Decimal("32.00"),
     "isbn": "978-7-5302-1029-1", "description": "反乌托邦经典，描绘了一个极权主义社会的恐怖景象。",
     "stock": 200, "publisher_name": "上海译文出版社", "category_names": ["外国文学", "世界名著", "科幻奇幻"]},
    {"book_name": "月亮与六便士", "author": "毛姆", "price": Decimal("39.00"),
     "isbn": "978-7-5327-8519-8", "description": "以高更为原型，描绘一个艺术家为理想抛弃一切的疯狂。",
     "stock": 150, "publisher_name": "上海译文出版社", "category_names": ["外国文学"]},
    {"book_name": "杀死一只知更鸟", "author": "哈珀·李", "price": Decimal("42.00"),
     "isbn": "978-7-5447-7650-1", "description": "普利策奖作品，关于种族、正义与成长的美国文学经典。",
     "stock": 180, "publisher_name": "上海译文出版社", "category_names": ["外国文学", "世界名著"]},

    # ═══════════ 科幻奇幻 ═══════════
    {"book_name": "银河帝国：基地", "author": "艾萨克·阿西莫夫", "price": Decimal("45.00"),
     "isbn": "978-7-5399-7910-8", "description": "科幻史最伟大的系列之一，心理史学的宏大预言。",
     "stock": 180, "publisher_name": "人民文学出版社", "category_names": ["科幻奇幻"]},
    {"book_name": "沙丘", "author": "弗兰克·赫伯特", "price": Decimal("68.00"),
     "isbn": "978-7-5399-5429-5", "description": "科幻史诗经典，沙漠星球上的政治、宗教与生态之战。",
     "stock": 140, "publisher_name": "人民文学出版社", "category_names": ["科幻奇幻", "外国文学"]},
    {"book_name": "哈利·波特与魔法石", "author": "J.K.罗琳", "price": Decimal("42.00"),
     "isbn": "978-7-02-010330-8", "description": "全球销量超5亿册的奇幻巨著，魔法世界的入门之书。",
     "stock": 300, "publisher_name": "人民文学出版社", "category_names": ["科幻奇幻", "外国文学"]},

    # ═══════════ 悬疑推理 ═══════════
    {"book_name": "嫌疑人X的献身", "author": "东野圭吾", "price": Decimal("39.50"),
     "isbn": "978-7-5442-4551-5", "description": "直木奖获奖作品，数学天才设下的完美不在场证明。",
     "stock": 220, "publisher_name": "上海译文出版社", "category_names": ["悬疑推理", "外国文学"]},
    {"book_name": "白夜行", "author": "东野圭吾", "price": Decimal("39.50"),
     "isbn": "978-7-5442-4550-8", "description": "东野圭吾巅峰之作，两个孩子在黑暗中相依为命的故事。",
     "stock": 200, "publisher_name": "上海译文出版社", "category_names": ["悬疑推理", "外国文学"]},
    {"book_name": "福尔摩斯探案全集", "author": "柯南·道尔", "price": Decimal("128.00"),
     "isbn": "978-7-5447-7889-4", "description": "推理小说史上最伟大的侦探，逻辑与观察的艺术。",
     "stock": 100, "publisher_name": "上海译文出版社", "category_names": ["悬疑推理", "世界名著"]},

    # ═══════════ 世界名著 ═══════════
    {"book_name": "战争与和平", "author": "列夫·托尔斯泰", "price": Decimal("98.00"),
     "isbn": "978-7-02-010288-8", "description": "托尔斯泰代表作，拿破仑战争时期的俄国社会全景图。",
     "stock": 90, "publisher_name": "人民文学出版社", "category_names": ["世界名著", "外国文学"]},
    {"book_name": "傲慢与偏见", "author": "简·奥斯汀", "price": Decimal("32.00"),
     "isbn": "978-7-5447-7682-2", "description": "英国文学史上最受欢迎的小说之一，机智幽默的爱情故事。",
     "stock": 180, "publisher_name": "上海译文出版社", "category_names": ["世界名著", "外国文学"]},

    # ═══════════ 人文社科：历史 ═══════════
    {"book_name": "万历十五年", "author": "黄仁宇", "price": Decimal("26.00"),
     "isbn": "978-7-108-00982-1", "description": "以1587年为切入点，揭示明朝由盛转衰的深层原因。",
     "stock": 180, "publisher_name": "三联书店", "category_names": ["历史"]},
    {"book_name": "人类简史", "author": "尤瓦尔·赫拉利", "price": Decimal("68.00"),
     "isbn": "978-7-5086-4735-7", "description": "从认知革命到科学革命，讲述智人如何成为地球的主宰。",
     "stock": 300, "publisher_name": "中信出版社", "category_names": ["历史", "社会学"]},
    {"book_name": "枪炮、病菌与钢铁", "author": "贾雷德·戴蒙德", "price": Decimal("55.00"),
     "isbn": "978-7-5086-4728-9", "description": "普利策奖作品，探讨人类社会命运差异的地理和生物根源。",
     "stock": 140, "publisher_name": "中信出版社", "category_names": ["历史", "社会学"]},
    {"book_name": "国史大纲", "author": "钱穆", "price": Decimal("88.00"),
     "isbn": "978-7-100-07464-5", "description": "钱穆先生的传世之作，对中国历史的温情与敬意。",
     "stock": 80, "publisher_name": "商务印书馆", "category_names": ["历史"]},
    {"book_name": "明朝那些事儿", "author": "当年明月", "price": Decimal("258.00"),
     "isbn": "978-7-213-08482-4", "description": "轻松幽默的笔调讲述明朝三百年的兴衰故事。",
     "stock": 250, "publisher_name": "北京大学出版社", "category_names": ["历史"]},

    # ═══════════ 哲学 ═══════════
    {"book_name": "苏菲的世界", "author": "乔斯坦·贾德", "price": Decimal("38.00"),
     "isbn": "978-7-5063-2816-2", "description": "以小说的形式讲述西方哲学史，全球畅销的哲学启蒙书。",
     "stock": 160, "publisher_name": "商务印书馆", "category_names": ["哲学"]},
    {"book_name": "存在与时间", "author": "马丁·海德格尔", "price": Decimal("78.00"),
     "isbn": "978-7-100-06099-9", "description": "20世纪最重要的哲学著作之一，重新定义了存在问题的意义。",
     "stock": 50, "publisher_name": "商务印书馆", "category_names": ["哲学"]},
    {"book_name": "中国哲学简史", "author": "冯友兰", "price": Decimal("49.00"),
     "isbn": "978-7-301-21570-1", "description": "冯友兰先生的哲学入门经典，提纲挈领地讲述中国哲学精神。",
     "stock": 120, "publisher_name": "北京大学出版社", "category_names": ["哲学"]},

    # ═══════════ 心理学 ═══════════
    {"book_name": "思考，快与慢", "author": "丹尼尔·卡尼曼", "price": Decimal("69.00"),
     "isbn": "978-7-5086-4355-7", "description": "诺贝尔经济学奖得主带你探索人类思维的两种模式。",
     "stock": 180, "publisher_name": "中信出版社", "category_names": ["心理学"]},
    {"book_name": "被讨厌的勇气", "author": "岸见一郎", "price": Decimal("45.00"),
     "isbn": "978-7-111-49548-2", "description": "阿德勒心理学通俗解读，教你如何获得真正的自由和幸福。",
     "stock": 250, "publisher_name": "机械工业出版社", "category_names": ["心理学"]},
    {"book_name": "社会性动物", "author": "艾略特·阿伦森", "price": Decimal("69.00"),
     "isbn": "978-7-5628-5151-5", "description": "社会心理学经典教材，用科学实验揭示人类行为的社会根源。",
     "stock": 100, "publisher_name": "机械工业出版社", "category_names": ["心理学", "社会学"]},

    # ═══════════ 社会学 ═══════════
    {"book_name": "乡土中国", "author": "费孝通", "price": Decimal("28.00"),
     "isbn": "978-7-100-06138-5", "description": "费孝通代表作，深刻揭示中国乡村社会的运行逻辑。",
     "stock": 200, "publisher_name": "商务印书馆", "category_names": ["社会学"]},
    {"book_name": "乌合之众", "author": "古斯塔夫·勒庞", "price": Decimal("29.00"),
     "isbn": "978-7-5117-2610-7", "description": "大众心理学经典，研究群体行为与集体无意识。",
     "stock": 180, "publisher_name": "商务印书馆", "category_names": ["社会学", "心理学"]},
    {"book_name": "未来简史", "author": "尤瓦尔·赫拉利", "price": Decimal("68.00"),
     "isbn": "978-7-5086-7206-6", "description": "从历史推演未来，人类将走向何方？",
     "stock": 200, "publisher_name": "中信出版社", "category_names": ["社会学", "历史"]},

    # ═══════════ 经济管理 ═══════════
    {"book_name": "原则", "author": "瑞·达利欧", "price": Decimal("98.00"),
     "isbn": "978-7-5086-5316-7", "description": "桥水基金创始人分享的人生和工作原则。",
     "stock": 150, "publisher_name": "中信出版社", "category_names": ["商业经管"]},
    {"book_name": "穷查理宝典", "author": "查理·芒格", "price": Decimal("88.00"),
     "isbn": "978-7-5086-5633-5", "description": "巴菲特搭档查理·芒格的智慧箴言录。",
     "stock": 180, "publisher_name": "中信出版社", "category_names": ["商业经管", "投资理财"]},
    {"book_name": "从0到1", "author": "彼得·蒂尔", "price": Decimal("45.00"),
     "isbn": "978-7-5086-4971-9", "description": "PayPal创始人讲述如何通过创新建立成功的公司。",
     "stock": 200, "publisher_name": "中信出版社", "category_names": ["商业经管"]},
    {"book_name": "薛兆丰经济学讲义", "author": "薛兆丰", "price": Decimal("68.00"),
     "isbn": "978-7-5086-8108-5", "description": "用经济学思维看世界，北大教授的经济学通识课。",
     "stock": 220, "publisher_name": "中信出版社", "category_names": ["经济学"]},
    {"book_name": "创新者的窘境", "author": "克莱顿·克里斯坦森", "price": Decimal("65.00"),
     "isbn": "978-7-5086-4282-6", "description": "为什么大公司会失败？颠覆式创新理论的经典之作。",
     "stock": 120, "publisher_name": "中信出版社", "category_names": ["商业经管"]},
    {"book_name": "小狗钱钱", "author": "博多·舍费尔", "price": Decimal("39.80"),
     "isbn": "978-7-5086-6108-7", "description": "写给孩子的理财启蒙书，同样适合成年人的理财第一课。",
     "stock": 250, "publisher_name": "中信出版社", "category_names": ["投资理财"]},
    {"book_name": "国富论", "author": "亚当·斯密", "price": Decimal("68.00"),
     "isbn": "978-7-100-06125-5", "description": "经济学开山之作，看不见的手与市场经济的理论基础。",
     "stock": 90, "publisher_name": "商务印书馆", "category_names": ["经济学"]},

    # ═══════════ 科学技术：编程语言 ═══════════
    {"book_name": "Python编程：从入门到实践", "author": "埃里克·马瑟斯", "price": Decimal("89.00"),
     "isbn": "978-7-115-54608-1", "description": "Python入门经典，手把手教你从零开始写项目。",
     "stock": 200, "publisher_name": "人民邮电出版社", "category_names": ["编程语言"]},
    {"book_name": "JavaScript高级程序设计", "author": "马特·弗里斯比", "price": Decimal("129.00"),
     "isbn": "978-7-115-54582-4", "description": "前端开发必读的红宝书，全面深入JavaScript核心。",
     "stock": 100, "publisher_name": "人民邮电出版社", "category_names": ["编程语言"]},
    {"book_name": "Rust程序设计", "author": "吉姆·布兰迪", "price": Decimal("99.00"),
     "isbn": "978-7-121-43012-1", "description": "系统编程语言的未来，零成本抽象和内存安全的完美结合。",
     "stock": 60, "publisher_name": "电子工业出版社", "category_names": ["编程语言"]},
    {"book_name": "Go语言程序设计", "author": "艾伦·多诺万", "price": Decimal("79.00"),
     "isbn": "978-7-111-56629-8", "description": "Go语言圣经，简洁高效的并发编程实战。",
     "stock": 90, "publisher_name": "机械工业出版社", "category_names": ["编程语言"]},

    # ═══════════ 数据库与存储 ═══════════
    {"book_name": "高性能MySQL", "author": "施瓦茨", "price": Decimal("128.00"),
     "isbn": "978-7-121-19032-1", "description": "MySQL性能优化的权威指南，DBA和开发者的案头必备。",
     "stock": 80, "publisher_name": "电子工业出版社", "category_names": ["数据库与存储"]},
    {"book_name": "Redis设计与实现", "author": "黄健宏", "price": Decimal("79.00"),
     "isbn": "978-7-111-47474-4", "description": "深入Redis内部数据结构与实现原理。",
     "stock": 90, "publisher_name": "机械工业出版社", "category_names": ["数据库与存储"]},

    # ═══════════ 云计算与架构 ═══════════
    {"book_name": "凤凰架构", "author": "周志明", "price": Decimal("99.00"),
     "isbn": "978-7-111-68766-5", "description": "构筑可靠的大型分布式系统，从单体到微服务的演进之路。",
     "stock": 120, "publisher_name": "机械工业出版社", "category_names": ["云计算与架构"]},
    {"book_name": "数据密集型应用系统设计", "author": "马丁·科勒普曼", "price": Decimal("139.00"),
     "isbn": "978-7-5198-5524-5", "description": "深入分布式系统的数据存储、处理和扩展。",
     "stock": 90, "publisher_name": "机械工业出版社", "category_names": ["云计算与架构", "数据库与存储"]},

    # ═══════════ 人工智能 ═══════════
    {"book_name": "深度学习", "author": "伊恩·古德费洛", "price": Decimal("168.00"),
     "isbn": "978-7-115-46147-8", "description": "深度学习领域奠基性经典教材，AI从业者必读。",
     "stock": 70, "publisher_name": "人民邮电出版社", "category_names": ["人工智能"]},
    {"book_name": "人工智能：一种现代方法", "author": "罗素", "price": Decimal("158.00"),
     "isbn": "978-7-302-48901-0", "description": "AI领域最权威的综合教材，全球千所大学选用。",
     "stock": 50, "publisher_name": "清华大学出版社", "category_names": ["人工智能"]},

    # ═══════════ 科普 ═══════════
    {"book_name": "时间简史", "author": "史蒂芬·霍金", "price": Decimal("45.00"),
     "isbn": "978-7-5357-5675-3", "description": "霍金带你探索宇宙的起源、黑洞和时间旅行的奥秘。",
     "stock": 200, "publisher_name": "商务印书馆", "category_names": ["科普"]},
    {"book_name": "上帝掷骰子吗", "author": "曹天元", "price": Decimal("49.00"),
     "isbn": "978-7-5477-1778-1", "description": "量子力学史话，用生动有趣的语言讲述量子物理的发展历程。",
     "stock": 150, "publisher_name": "北京大学出版社", "category_names": ["科普"]},
    {"book_name": "自私的基因", "author": "理查德·道金斯", "price": Decimal("55.00"),
     "isbn": "978-7-5086-9449-3", "description": "从基因的角度重新理解进化，颠覆你对生命的认知。",
     "stock": 130, "publisher_name": "中信出版社", "category_names": ["科普"]},
    {"book_name": "从一到无穷大", "author": "乔治·伽莫夫", "price": Decimal("38.00"),
     "isbn": "978-7-03-052847-6", "description": "科学入门经典，用幽默的语言带你漫游数学与物理的世界。",
     "stock": 140, "publisher_name": "商务印书馆", "category_names": ["科普"]},

    # ═══════════ 生活休闲 ═══════════
    {"book_name": "舌尖上的中国", "author": "中央电视台纪录频道", "price": Decimal("50.00"),
     "isbn": "978-7-5112-3186-7", "description": "同名纪录片图书版，展现中国饮食文化的深厚底蕴。",
     "stock": 100, "publisher_name": "中信出版社", "category_names": ["美食烹饪"]},
    {"book_name": "孤独美食家", "author": "村上龙", "price": Decimal("35.00"),
     "isbn": "978-7-5404-6372-2", "description": "三十二个城市、三十二道美食、三十二段人生故事。",
     "stock": 120, "publisher_name": "上海译文出版社", "category_names": ["美食烹饪", "外国文学"]},
    {"book_name": "Lonely Planet：中国", "author": "Lonely Planet公司", "price": Decimal("128.00"),
     "isbn": "978-7-5032-5434-4", "description": "全球旅行者的圣经，中国旅行完全指南。",
     "stock": 80, "publisher_name": "三联书店", "category_names": ["旅游地理"]},
    {"book_name": "断舍离", "author": "山下英子", "price": Decimal("32.00"),
     "isbn": "978-7-5086-5338-0", "description": "通过整理物品来整理内心，风靡全球的生活哲学。",
     "stock": 180, "publisher_name": "中信出版社", "category_names": ["健康养生"]},

    # ═══════════ 艺术设计 ═══════════
    {"book_name": "写给大家看的设计书", "author": "罗宾·威廉姆斯", "price": Decimal("59.00"),
     "isbn": "978-7-115-44188-2", "description": "设计入门经典，零基础也能理解四大基本原则。",
     "stock": 150, "publisher_name": "人民邮电出版社", "category_names": ["绘画书法"]},
    {"book_name": "美的历程", "author": "李泽厚", "price": Decimal("48.00"),
     "isbn": "978-7-108-03749-3", "description": "中国美学史的开创性著作，从远古到明清的艺术巡礼。",
     "stock": 100, "publisher_name": "三联书店", "category_names": ["绘画书法"]},
    {"book_name": "艺术的故事", "author": "贡布里希", "price": Decimal("280.00"),
     "isbn": "978-7-5494-5561-0", "description": "全球最畅销的艺术入门书，从洞穴壁画到现代艺术。",
     "stock": 50, "publisher_name": "三联书店", "category_names": ["绘画书法"]},
    {"book_name": "美国纽约摄影学院摄影教材", "author": "美国纽约摄影学院", "price": Decimal("98.00"),
     "isbn": "978-7-5179-0687-2", "description": "摄影爱好者必读经典，从器材使用到构图用光的全面指南。",
     "stock": 70, "publisher_name": "人民邮电出版社", "category_names": ["摄影"]},
    # ═══════════ 补充：各分类更多真实书籍 ═══════════
    {"book_name": "解忧杂货店", "author": "东野圭吾", "price": Decimal("39.50"),
     "isbn": "978-7-5442-6952-5", "description": "一家能穿越时空的杂货店，连接过去与现在的温暖故事。",
     "stock": 280, "publisher_name": "上海译文出版社", "category_names": ["外国文学", "悬疑推理"]},
    {"book_name": "小王子", "author": "圣埃克苏佩里", "price": Decimal("22.00"),
     "isbn": "978-7-02-010455-3", "description": "全球发行量仅次于圣经的经典童话，关于爱与责任。",
     "stock": 350, "publisher_name": "人民文学出版社", "category_names": ["世界名著", "外国文学"]},
    {"book_name": "了不起的盖茨比", "author": "菲茨杰拉德", "price": Decimal("29.80"),
     "isbn": "978-7-5447-5432-1", "description": "美国爵士时代的挽歌，关于美国梦的破灭。",
     "stock": 160, "publisher_name": "上海译文出版社", "category_names": ["世界名著", "外国文学"]},
    {"book_name": "霍乱时期的爱情", "author": "加西亚·马尔克斯", "price": Decimal("49.00"),
     "isbn": "978-7-5442-7223-4", "description": "马尔克斯自认最好的作品，跨越半个世纪的爱情史诗。",
     "stock": 130, "publisher_name": "上海译文出版社", "category_names": ["外国文学", "世界名著"]},
    {"book_name": "局外人", "author": "阿尔贝·加缪", "price": Decimal("25.00"),
     "isbn": "978-7-5327-5530-9", "description": "存在主义文学经典，冷漠背后的真实与荒诞。",
     "stock": 170, "publisher_name": "上海译文出版社", "category_names": ["外国文学", "世界名著", "哲学"]},
    {"book_name": "动物农场", "author": "乔治·奥威尔", "price": Decimal("25.00"),
     "isbn": "978-7-5327-4029-4", "description": "一座农场里的革命寓言，极权主义的深刻讽刺。",
     "stock": 200, "publisher_name": "上海译文出版社", "category_names": ["外国文学", "世界名著"]},
    {"book_name": "人间失格", "author": "太宰治", "price": Decimal("25.00"),
     "isbn": "978-7-5063-5947-4", "description": "日本文学史上最具冲击力的私小说，绝望中的自白。",
     "stock": 190, "publisher_name": "人民文学出版社", "category_names": ["外国文学"]},
    {"book_name": "呼兰河传", "author": "萧红", "price": Decimal("28.00"),
     "isbn": "978-7-02-010170-0", "description": "萧红最后的作品，用诗意的笔触描绘东北小城的人情冷暖。",
     "stock": 130, "publisher_name": "人民文学出版社", "category_names": ["中国文学"]},
    {"book_name": "尘埃落定", "author": "阿来", "price": Decimal("38.00"),
     "isbn": "978-7-02-009640-0", "description": "茅盾文学奖作品，一个藏族土司家族的兴衰史诗。",
     "stock": 100, "publisher_name": "人民文学出版社", "category_names": ["中国文学"]},
    {"book_name": "明朝那些事儿·第一部", "author": "当年明月", "price": Decimal("39.80"),
     "isbn": "978-7-213-04672-1", "description": "从朱元璋的童年讲起，幽默笔调写尽大明开国风云。",
     "stock": 300, "publisher_name": "北京大学出版社", "category_names": ["历史"]},
    {"book_name": "全球通史", "author": "斯塔夫里阿诺斯", "price": Decimal("98.00"),
     "isbn": "978-7-301-15556-7", "description": "最畅销的全球史著作，打破欧洲中心论的宏大叙事。",
     "stock": 110, "publisher_name": "北京大学出版社", "category_names": ["历史"]},
    {"book_name": "浪潮之巅", "author": "吴军", "price": Decimal("69.00"),
     "isbn": "978-7-115-28288-8", "description": "讲述IT产业发展的历史浪潮，科技公司的兴衰启示录。",
     "stock": 180, "publisher_name": "人民邮电出版社", "category_names": ["历史", "商业经管"]},
    {"book_name": "正念的奇迹", "author": "一行禅师", "price": Decimal("32.00"),
     "isbn": "978-7-5117-1234-8", "description": "一行禅师关于正念修行的通俗入门书。",
     "stock": 160, "publisher_name": "中信出版社", "category_names": ["哲学", "心理学"]},
    {"book_name": "非暴力沟通", "author": "马歇尔·卢森堡", "price": Decimal("39.00"),
     "isbn": "978-7-5080-5523-1", "description": "一种基于同理心的沟通方式，改善人际关系。",
     "stock": 220, "publisher_name": "机械工业出版社", "category_names": ["心理学"]},
    {"book_name": "刻意练习", "author": "安德斯·艾利克森", "price": Decimal("49.00"),
     "isbn": "978-7-111-55128-6", "description": "如何从新手到大师？一万小时理论的科学升级版。",
     "stock": 200, "publisher_name": "机械工业出版社", "category_names": ["心理学"]},
    {"book_name": "影响力", "author": "罗伯特·西奥迪尼", "price": Decimal("55.00"),
     "isbn": "978-7-5502-0032-5", "description": "说服心理学的经典之作，揭示顺从行为的六大原则。",
     "stock": 220, "publisher_name": "中信出版社", "category_names": ["心理学", "市场营销"]},
    {"book_name": "富爸爸穷爸爸", "author": "罗伯特·清崎", "price": Decimal("39.00"),
     "isbn": "978-7-220-10761-8", "description": "全球畅销的理财启蒙书，改变你对金钱的认知。",
     "stock": 300, "publisher_name": "中信出版社", "category_names": ["投资理财"]},
    {"book_name": "定位", "author": "杰克·特劳特", "price": Decimal("42.00"),
     "isbn": "978-7-111-32640-5", "description": "有史以来对美国营销影响最大的观念。",
     "stock": 120, "publisher_name": "机械工业出版社", "category_names": ["市场营销"]},
    {"book_name": "重构：改善既有代码的设计", "author": "马丁·福勒", "price": Decimal("99.00"),
     "isbn": "978-7-115-50559-2", "description": "软件开发必读经典，系统性地改善代码质量。",
     "stock": 130, "publisher_name": "人民邮电出版社", "category_names": ["编程语言"]},
    {"book_name": "程序员的自我修养", "author": "俞甲子", "price": Decimal("65.00"),
     "isbn": "978-7-121-08510-0", "description": "链接、装载与库深入解析，理解程序运行的底层原理。",
     "stock": 80, "publisher_name": "电子工业出版社", "category_names": ["编程语言"]},
    {"book_name": "代码整洁之道", "author": "罗伯特·马丁", "price": Decimal("59.00"),
     "isbn": "978-7-115-52162-0", "description": "Clean Code中文版，写出让同事感激的高质量代码。",
     "stock": 160, "publisher_name": "人民邮电出版社", "category_names": ["编程语言"]},
    {"book_name": "Kubernetes权威指南", "author": "龚正", "price": Decimal("129.00"),
     "isbn": "978-7-121-46350-9", "description": "Kubernetes生产级实践指南，从入门到精通。",
     "stock": 80, "publisher_name": "电子工业出版社", "category_names": ["云计算与架构"]},
    {"book_name": "信息简史", "author": "詹姆斯·格雷克", "price": Decimal("69.00"),
     "isbn": "978-7-115-33180-6", "description": "从非洲鼓语到云计算，信息的演化史就是人类文明史。",
     "stock": 90, "publisher_name": "人民邮电出版社", "category_names": ["科普", "历史"]},
    {"book_name": "万物简史", "author": "比尔·布莱森", "price": Decimal("49.00"),
     "isbn": "978-7-5448-3230-5", "description": "用幽默的语言讲述科学史上最伟大的发现。",
     "stock": 150, "publisher_name": "北京大学出版社", "category_names": ["科普"]},
    {"book_name": "蔡澜旅行食记", "author": "蔡澜", "price": Decimal("45.00"),
     "isbn": "978-7-5552-2687-3", "description": "香港四大才子之一的美食旅行笔记。",
     "stock": 120, "publisher_name": "三联书店", "category_names": ["美食烹饪", "旅游地理"]},
    {"book_name": "小家，越住越大", "author": "逯薇", "price": Decimal("58.00"),
     "isbn": "978-7-5086-6859-9", "description": "为中国人量身定制的居家收纳术。",
     "stock": 200, "publisher_name": "中信出版社", "category_names": ["家居园艺"]},
    {"book_name": "认识建筑", "author": "罗伯特·麦卡特", "price": Decimal("198.00"),
     "isbn": "978-7-5356-9324-2", "description": "从古罗马到今天，通过72座建筑理解空间与文明。",
     "stock": 40, "publisher_name": "北京大学出版社", "category_names": ["建筑"]},
    {"book_name": "聆听音乐", "author": "克雷格·莱特", "price": Decimal("88.00"),
     "isbn": "978-7-108-06661-1", "description": "耶鲁大学公开课教材，零基础听懂古典音乐。",
     "stock": 80, "publisher_name": "三联书店", "category_names": ["音乐"]},
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
            print(f"✅ 插入了 {len(CATEGORIES_TREE)} 个顶级分类及其子分类")
        else:
            print(f"⏭️  分类数据已存在，跳过")

        # ── 书籍 ──
        existing = await session.execute(select(func.count(Book.id)))
        if existing.scalar() == 0:
            pub_result = await session.execute(select(Publisher))
            publishers_map = {p.name: p for p in pub_result.scalars().all()}
            cat_result = await session.execute(select(Category))
            categories_map = {c.name: c for c in cat_result.scalars().all()}

            # 1) 精选书籍
            for item in BOOKS_DATA:
                category_names = item.pop("category_names", [])
                pub_name = item.pop("publisher_name", None)
                item["publisher_id"] = publishers_map[pub_name].id if pub_name in publishers_map else None
                book = Book(**item)
                for cname in category_names:
                    if cname in categories_map:
                        book.categories.append(categories_map[cname])
                session.add(book)
            await session.flush()
            print(f"✅ 插入 {len(BOOKS_DATA)} 本精选书籍")

            # 2) 批量生成（目标 300 本）
            TARGET = 250
            to_gen = TARGET - len(BOOKS_DATA)

            all_publishers = list(publishers_map.values())
            all_categories = list(categories_map.values())

            # 按分类领域设定书名词库，使生成的书名更真实
            TITLE_PARTS = {
                "文学小说": {
                    "prefixes": ["", "", "", "我的", "消失的", "漫长的", "最后的", "寂静的", "远方的", "孤独的"],
                    "suffixes": ["时光", "岁月", "季节", "告白", "旅程", "世界", "告别", "记忆", "答案", "命运"],
                },
                "人文社科": {
                    "prefixes": ["", "", "理解", "解读", "重新发现", "探索", "反思"],
                    "suffixes": ["社会", "文明", "时代", "秩序", "制度", "思想史", "简史", "的逻辑", "的力量"],
                },
                "经济管理": {
                    "prefixes": ["", "创新", "增长", "颠覆", "高效", "敏捷", "精益"],
                    "suffixes": ["之道", "法则", "方法论", "实战", "从入门到精通", "思维", "领导力", "商业模式"],
                },
                "科学技术": {
                    "prefixes": ["深入理解", "精通", "实战", "权威指南", "从零开始学", "深入浅出", "高级"],
                    "suffixes": ["编程", "系统设计", "架构", "算法", "网络", "安全", "数据分析", "工程实践"],
                },
                "生活休闲": {
                    "prefixes": ["", "轻松", "幸福", "美好", "品质"],
                    "suffixes": ["生活", "的艺术", "笔记", "日记", "手记", "小时光", "慢生活", "很简单"],
                },
                "艺术设计": {
                    "prefixes": ["", "大师", "经典", "现代"],
                    "suffixes": ["设计", "美学", "配色", "手绘", "创意", "风格", "鉴赏", "入门"],
                },
            }

            AUTHORS = [
                "张志明", "李思远", "王海峰", "赵晓娟", "陈建国", "刘雨彤", "周明哲",
                "吴晓琳", "孙浩然", "钱一鸣", "杨雪晴", "黄文斌", "林清和", "郑慧敏",
                "田中裕子", "山本健太", "David Chen", "Sarah Wang", "James Liu",
            ]

            for i in range(to_gen):
                # 随机选一个分类，根据分类领域选词库
                cat = random.choice(all_categories)
                # 找到该分类的顶级领域
                domain_parts = TITLE_PARTS.get("科学技术", TITLE_PARTS["文学小说"])
                for domain, parts in TITLE_PARTS.items():
                    top_cats = [c for c in all_categories if c.parent_id == cat.parent_id]
                    # 简化：随机选领域
                    domain = random.choice(list(TITLE_PARTS.keys()))
                    domain_parts = TITLE_PARTS[domain]

                prefix = random.choice(domain_parts["prefixes"])
                suffix = random.choice(domain_parts["suffixes"])
                title = f"{prefix}{suffix}".strip()
                if not title:
                    title = f"未命名书籍{i+1}"

                book = Book(
                    book_name=title,
                    author=random.choice(AUTHORS),
                    price=Decimal(str(round(random.uniform(20, 150), 2))),
                    publisher_id=random.choice(all_publishers).id,
                    stock=random.randint(0, 200),
                )
                num_cats = random.randint(1, 3)
                book.categories = random.sample(all_categories, min(num_cats, len(all_categories)))
                session.add(book)

            await session.commit()
            print(f"✅ 批量生成 {to_gen} 本，总计 {TARGET} 本书籍")
        else:
            print(f"⏭️  书籍数据已存在，跳过")

        await session.commit()
        print("\n🎉 所有种子数据初始化完成")

if __name__ == "__main__":
    asyncio.run(seed_all())
