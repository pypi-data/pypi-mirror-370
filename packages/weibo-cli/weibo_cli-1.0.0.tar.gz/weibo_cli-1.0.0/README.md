# 微博 API 客户端

高性能的微博 API 客户端，采用 **Facade Pattern** 和 **防腐层模式**，提供类型安全的微博数据获取功能。

## ✨ 特性

- 🏗️ **Facade Pattern**: 简化的高级API接口，隐藏底层复杂性
- 🛡️ **防腐层 (Anti-Corruption Layer)**: 隔离外部API变化，提供数据映射和验证
- 🔒 **类型安全**: 强类型的 Pydantic 模型，IDE 自动补全和类型检查
- 🚀 **同步 & 异步支持**: 提供 `WeiboClient` 和 `AsyncWeiboClient` 两种客户端
- 🔧 **底层访问**: 可直接使用 `AsyncWeiboRawClient` 获取原始JSON数据
- 🛡️ **完善的错误处理**: 统一的异常体系，包含网络错误、认证错误、速率限制等
- 🔄 **自动重试机制**: 内置指数退避重试策略，提高请求成功率
- 🚦 **智能速率限制**: 自动控制请求频率，避免触发服务器限制
- 📊 **数据模型验证**: 使用 Pydantic 进行数据验证和序列化
- 🍪 **自动 Cookie 管理**: 自动获取和管理访客 Cookie
- ⚙️ **灵活配置**: 支持自定义超时、重试、速率限制等参数
- 🧪 **完整测试覆盖**: 包含单元测试和集成测试

## 📦 安装

### (推荐,可选) 使用 UV
```bash
curl -fsSL -o /tmp/uv-installer.sh https://astral.sh/uv/install.sh && \
    sh /tmp/uv-installer.sh && \
    rm /tmp/uv-installer.sh
```

### 安装开发环境
```bash
uv pip install -e ".[dev]"
uv pip install -e ".[test]"
```

## 🚀 快速开始

### Fast Eaxmple

运行最简单的使用示例:
```bash
# 使用传统 Python
python main.py
# 或者使用 UV
uv run main.py
```

运行 `pytest` 测试用例. 
```bash
# 使用传统 Python
python -m pytest -v
# 或者使用 UV
uv run pytest -v
uv run pytest --cov -v # 带覆盖率报告
```

### 同步客户端

```python
from weibo_api import WeiboClient

# 创建客户端
client = WeiboClient()

# 获取用户信息
user_data = client.get_user_profile("1749127163")  # 雷军的用户ID
print(user_data)

# 获取用户时间线
timeline = client.get_user_timeline("1749127163", page=1)
print(timeline)

# 获取微博详情
detail = client.get_weibo_detail("微博ID")
print(detail)

# 获取微博评论
comments = client.get_weibo_comments("微博ID")
print(comments)
```

### 异步客户端 (Facade Pattern)

```python
import asyncio
from weibo_api import AsyncWeiboClient
from weibo_api.models import WeiboUser, WeiboPost

async def main():
    # 创建异步客户端 (Facade层)
    client = AsyncWeiboClient()

    # 异步获取用户信息 - 返回强类型的WeiboUser对象
    user: WeiboUser = await client.get_user_profile("1749127163")
    print(f"用户名: {user.screen_name}")
    print(f"粉丝数: {user.followers_count:,}")
    print(f"认证状态: {user.verified}")

    # 异步获取用户时间线 - 返回WeiboPost列表
    posts: list[WeiboPost] = await client.get_user_timeline("1749127163", page=1)
    print(f"获取到 {len(posts)} 条微博")

    if posts:
        latest_post = posts[0]
        print(f"最新微博: {latest_post.text[:50]}...")
        print(f"点赞数: {latest_post.attitudes_count}")

    # 并发获取多个用户信息
    user_ids = ["1749127163", "1749127163"]
    tasks = [client.get_user_profile(uid) for uid in user_ids]
    users: list[WeiboUser] = await asyncio.gather(*tasks)

    for user in users:
        print(f"用户: {user.screen_name}")

# 运行异步代码
asyncio.run(main())
```

### 底层原始客户端 (高级用法)

```python
import asyncio
from weibo_api import AsyncWeiboRawClient

async def main():
    # 创建原始客户端 (直接访问底层API)
    raw_client = AsyncWeiboRawClient()

    # 获取原始JSON数据
    raw_data = await raw_client.get_user_profile("1749127163")
    print(f"原始数据: {raw_data}")

    # 可以访问Facade层未暴露的字段
    if "data" in raw_data:
        user_data = raw_data["data"]["user"]
        print(f"所有字段: {list(user_data.keys())}")

asyncio.run(main())
```

## 🏗️ 架构设计

本项目采用 **Facade Pattern** 和 **防腐层模式** 的分层架构：

```
┌─────────────────────────────────────────┐
│           AsyncWeiboClient              │  ← Facade层 (推荐使用)
│  ┌─────────────────────────────────────┐ │
│  │     高级业务接口                      │ │
│  │  - get_user_profile() → WeiboUser   │ │
│  │  - get_user_timeline() → List[Post] │ │
│  │  - get_weibo_detail() → WeiboPost   │ │
│  │  - get_weibo_comments() → Comments  │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│              Mapper层                   │  ← 防腐层
│  ┌─────────────────────────────────────┐ │
│  │     数据转换与验证                    │ │
│  │  - RawDTO → BusinessModel           │ │
│  │  - 数据清洗与标准化                   │ │
│  │  - 异常处理与容错                     │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         AsyncWeiboRawClient             │  ← 底层客户端
│  ┌─────────────────────────────────────┐ │
│  │     底层API调用                      │ │
│  │  - HTTP请求处理                      │ │
│  │  - Cookie管理                       │ │
│  │  - 速率限制                          │ │
│  │  - 返回原始JSON                      │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 层次说明

- **Facade层**: 提供简化的高级API，返回强类型的Pydantic模型
- **防腐层**: 隔离外部API变化，处理数据映射和验证
- **底层客户端**: 直接处理HTTP请求，返回原始JSON数据

### 使用建议

- **日常开发**: 使用 `AsyncWeiboClient` (Facade层)
- **特殊需求**: 使用 `AsyncWeiboRawClient` (底层访问)
- **混合使用**: 通过 `client.raw_client` 访问底层客户端

## ⚙️ 配置

### 基本配置

```python
from weibo_api import WeiboClient, WeiboConfig

# 自定义配置
config = WeiboConfig(
    timeout=15.0,           # 请求超时时间
    max_retries=3,          # 最大重试次数
    retry_delay=1.0,        # 重试延迟
    rate_limit_calls=100,   # 速率限制：请求次数
    rate_limit_window=60,   # 速率限制：时间窗口（秒）
)

client = WeiboClient(config=config)
```

### 预设配置

```python
# 快速配置（适用于测试）
fast_config = WeiboConfig.create_fast_config()
client = WeiboClient(config=fast_config)

# 保守配置（适用于生产环境）
conservative_config = WeiboConfig.create_conservative_config()
client = WeiboClient(config=conservative_config)
```

## 📊 数据模型

### Facade层 - 强类型模型 (推荐)

Facade层自动返回强类型的Pydantic模型，提供类型安全和IDE支持：

```python
from weibo_api import AsyncWeiboClient
from weibo_api.models import WeiboUser, WeiboPost, WeiboComment

async def main():
    client = AsyncWeiboClient()

    # 获取用户信息 - 自动返回WeiboUser对象
    user: WeiboUser = await client.get_user_profile("1749127163")
    print(f"用户名: {user.screen_name}")           # IDE自动补全
    print(f"粉丝数: {user.followers_count:,}")     # 类型安全
    print(f"认证状态: {user.verified}")            # 布尔类型

    # 获取时间线 - 自动返回WeiboPost列表
    posts: list[WeiboPost] = await client.get_user_timeline("1749127163")

    for post in posts:
        print(f"微博: {post.text[:50]}...")
        print(f"点赞: {post.attitudes_count}")
        print(f"作者: {post.user.screen_name}")    # 嵌套对象

        # 处理图片 - 类型安全的图片访问
        for image in post.images:
            print(f"缩略图: {image.thumbnail.url}")
            print(f"大图: {image.large.url}")
            print(f"原图: {image.original.url}")
```

### 底层访问 - 原始JSON数据

需要访问原始数据或未暴露字段时：

```python
from weibo_api import AsyncWeiboRawClient
from weibo_api.models import UserDetailResponse

async def main():
    raw_client = AsyncWeiboRawClient()

    # 获取原始JSON数据
    raw_data = await raw_client.get_user_profile("1749127163")

    # 手动解析 (可选)
    if raw_data and raw_data.get("ok") == 1:
        user_response = UserDetailResponse.model_validate(raw_data)
        user = user_response.data.user
        print(f"用户名: {user.screen_name}")

    # 或直接使用原始数据
    user_data = raw_data["data"]["user"]
    print(f"所有字段: {list(user_data.keys())}")
```

## 🛡️ 错误处理

```python
from weibo_api.exceptions import (
    WeiboError, NetworkError, AuthenticationError, 
    RateLimitError, ParseError
)

try:
    result = client.get_user_profile("用户ID")
except NetworkError as e:
    print(f"网络错误: {e}")
except AuthenticationError as e:
    print(f"认证错误: {e}")
except RateLimitError as e:
    print(f"速率限制: {e}")
except ParseError as e:
    print(f"解析错误: {e}")
except WeiboError as e:
    print(f"微博API错误: {e}")
```

## 🔧 工具函数

```python
from weibo_api.utils import (
    validate_user_id, validate_weibo_id,
    clean_text, format_count, is_valid_cookie
)

# 验证ID格式
if validate_user_id("1749127163"):
    print("用户ID格式正确")

# 格式化数字
print(format_count(1234567))  # 输出: 123.5万

# 清理文本
clean_content = clean_text("  包含多余空格的文本  ")

# 验证Cookie
if is_valid_cookie("SUB=xxx; SUBP=yyy"):
    print("Cookie格式正确")
```

## 📁 项目结构

```
weibo_api/
├── __init__.py              # 模块入口
├── client.py                # 同步客户端
├── async_client.py          # 异步原始客户端 (AsyncWeiboRawClient)
├── facade_client.py         # 异步Facade客户端 (AsyncWeiboClient)
├── mapper.py                # 数据映射器 (防腐层)
├── config.py                # 配置管理
├── exceptions.py            # 异常定义
├── models.py                # 数据模型 (业务模型 + DTO模型)
├── utils.py                 # 工具函数
├── examples/                # 使用示例
│   ├── basic_usage.py       # 基本使用
│   ├── async_usage.py       # 异步使用
│   ├── advanced_usage.py    # 高级功能
│   └── facade_pattern_demo.py # Facade Pattern演示
└── tests/                   # 测试文件
    ├── test_models.py       # 数据模型测试
    ├── test_mapper.py       # 映射器测试
    ├── test_utils.py        # 工具函数测试
    ├── test_client.py       # 同步客户端测试
    ├── test_async_client.py # 原始客户端测试
    ├── test_facade_client.py # Facade客户端测试
    └── test_integration.py  # 集成测试
```

## 🧪 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest weibo_api/tests/

# 运行单元测试
pytest weibo_api/tests/test_models.py
pytest weibo_api/tests/test_utils.py

# 运行集成测试（需要网络连接）
pytest weibo_api/tests/test_integration.py -m integration
```

## 📚 示例

查看 `examples/` 目录中的完整示例：

- `basic_usage.py` - 基本功能演示
- `async_usage.py` - 异步和并发使用 (已更新为Facade API)
- `advanced_usage.py` - 高级功能和最佳实践
- `facade_pattern_demo.py` - **新增**: Facade Pattern架构演示

### 运行示例

```bash
# Facade Pattern演示 (推荐先看这个)
python weibo_api/examples/facade_pattern_demo.py

# 异步使用演示
python weibo_api/examples/async_usage.py

# 基本使用演示
python weibo_api/examples/basic_usage.py
```

## ⚠️ 注意事项

1. **遵守服务条款**: 请遵守微博的服务条款和使用限制
2. **速率限制**: 合理设置请求频率，避免对服务器造成压力
3. **错误处理**: 始终处理可能的异常情况
4. **数据使用**: 仅用于合法目的，尊重用户隐私

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [微博开放平台](https://open.weibo.com/)
- [Pydantic 文档](https://pydantic-docs.helpmanual.io/)
- [HTTPX 文档](https://www.python-httpx.org/)
