# JCWeaver 简介

**JCWeaver** 是一个面向 *云际异构环境* 的轻量级编程模型工具库，旨在帮助开发者屏蔽不同平台之间的差异，实现 **统一的数据封装与平台适配**。

通过简单的代码修饰，开发者即可专注于核心业务逻辑，无需关注繁杂的平台集成细节。

---

# JCWeaver 代码架构

项目结构如下：

```
jcweaver/
├── __init__.py
├── api/                    # 面向用户的主 API 模块
│   ├── __init__.py
│   ├── api.py              # 主入口 API
│   └── decorators.py       # 任务与函数的装饰器定义
├── core/                   # 内部核心机制
│   ├── __init__.py
│   ├── registry.py         # 任务注册与元数据管理
│   ├── schema.py           # 输入输出数据结构定义
│   ├── logger.py           # 日志系统
│   ├── context.py          # 上下文管理（运行时状态）
│   ├── metadata.py         # 元信息定义
├── adapter/                # 平台适配层
│   ├── __init__.py
│   └── openi.py            # OpenI 平台适配实现
├── cli/                    # 命令行工具（可选，开发中）
└── tests/                  # 单元测试目录
```

# 使用JCWeaver
```
pip install jcweaver --index-url https://pypi.org/simple
```