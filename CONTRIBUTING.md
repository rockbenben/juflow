# 为 JuFlow 贡献代码

本地开发环境的搭建见 [README 的「开发指南」](README.md#开发指南)。这里是写适配器插件和项目结构的详细说明。

## 编写适配器插件

适配器通过基类实现，只需声明配置。三种基类可选：

**RSSHub 适配器**（最简单，推荐优先使用）：

```python
# adapter.py
from app.adapters.rsshub_base import RsshubBaseAdapter

class MyAdapter(RsshubBaseAdapter):
    platform = "myplatform"
    name = "我的平台"
    url_pattern = r"https?://myplatform\.com/user/(\w+)"
    rsshub_route_template = "/myplatform/user/{uid}"
    display_name_template = "用户{uid}"
    home_url_template = "https://myplatform.com/user/{uid}"
```

**直接 RSS 适配器**：

```python
from app.adapters.rss_base import DirectRssBaseAdapter

class MyAdapter(DirectRssBaseAdapter):
    platform = "myplatform"
    name = "我的平台"
    url_pattern = r"https?://myplatform\.com/blog/(\w+)"
    rss_url_template = "https://myplatform.com/blog/{uid}/rss"
    home_url_template = "https://myplatform.com/blog/{uid}"
```

**爬虫适配器**（`title` 和 `summary` 支持 `|` 分隔的优先级回退，如 `"a.title|a"` 表示优先找 `a.title`，找不到则回退到 `a`）：

```python
from app.adapters.scraper_base import ScraperBaseAdapter, ScraperSelectors

class MyAdapter(ScraperBaseAdapter):
    platform = "myplatform"
    name = "我的平台"
    url_pattern = r"https?://myplatform\.com/u/(\w+)"
    profile_url_template = "https://myplatform.com/u/{uid}"
    selectors = ScraperSelectors(
        item=".post-item",
        title="a.title|a",
        summary=".summary|p",
        url_prefix="https://myplatform.com",
    )
```

每个插件还需要一个 `manifest.json`：

```json
{
  "name": "myplatform",
  "display_name": "我的平台",
  "version": "1.0.0",
  "author": "your-name",
  "description": "我的平台适配器",
  "adapter_class": "MyAdapter"
}
```

## 项目结构

```text
juflow/
├── backend/
│   ├── app/
│   │   ├── adapters/       # 平台适配器（3 个基类 + 14 个内置 + 插件加载）
│   │   ├── api/            # FastAPI 路由
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 验证模型
│   │   ├── services/       # 业务逻辑 + 通知渠道
│   │   ├── tasks/          # Celery 异步任务（worker 进程内共享独立连接池 app/tasks/db）
│   │   ├── config.py       # 配置
│   │   ├── database.py     # 数据库连接
│   │   └── main.py         # FastAPI 入口
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试
│   ├── entrypoint.sh       # 启动前自动迁移
│   ├── Dockerfile          # 多阶段构建，非 root 用户
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue 组件（含新用户引导、设置面板）
│   │   ├── composables/    # 组合式函数（主题/快捷键/WebSocket+Toast/平台色与抓取间隔）
│   │   ├── i18n/           # 国际化（zh-CN / en）
│   │   ├── stores/         # Pinia 状态管理
│   │   └── views/          # 页面视图
│   ├── Dockerfile          # 多阶段构建 + 健康检查
│   └── nginx.conf          # 反向代理 + gzip
├── postgres/
│   └── init.sql            # 数据库初始化脚本
├── plugins/adapters/       # 社区插件目录
├── .github/workflows/      # CI（pytest + 前端构建）
├── docker-compose.yml      # 生产配置（无暴露 DB 端口）
├── docker-compose.override.yml  # 开发端口暴露（compose 自动加载）
├── setup.sh              # 部署引导：生成 .env 并填充随机密钥（POSIX shell）
├── .env.example
├── .gitattributes          # 强制 shell/Dockerfile LF 换行
└── README.md
```

