# 聚流 JuFlow

国内博主内容聚合阅读器。关注的博主发的文章实时推送，覆盖雪球、集思录、淘股吧、微信公众号、知乎、微博、小红书等 14 个平台。

## 为什么做这个

Folo 等 RSS 阅读器对国内个人博主支持不足。很多平台没有 RSS 输出，需要爬虫才能抓取内容。聚流通过混合适配器架构（RSS → RSSHub → 自定义爬虫）自动选择最优抓取方式，让你一个入口读到所有关注博主的更新。

## 功能特性

### 内容聚合
- **14 个平台**：雪球、集思录、淘股吧、东方财富、同花顺、韭圈儿、有知有行、微信公众号、知乎、微博、小红书、掘金、CSDN、V2EX
- **粘贴链接订阅**：粘贴博主主页 URL，系统自动识别平台
- **新用户引导**：注册后推荐高质量博主，一键批量订阅
- **OPML 导入/导出**：从其他阅读器迁移订阅
- **可配置抓取频率**：1 分钟到 30 分钟，按订阅源独立设置
- **插件市场**：社区贡献适配器，动态安装（仅管理员可安装，worker 需重启生效）

### 阅读体验
- **三栏布局**：侧边栏 + 文章列表 + 阅读面板（桌面端）
- **移动端适配**：响应式单栏布局 + 底部导航
- **安全渲染**：文章内容通过 DOMPurify 净化后展示
- **分组/标签**：自定义文件夹和彩色标签组织订阅
- **收藏 + 稍后阅读**
- **标题搜索**：关键词模糊匹配
- **键盘快捷键**：j/k 导航、s 收藏、m 已读、? 帮助
- **暗色/亮色主题**：支持跟随系统

### 实时推送
- **WebSocket**：站内实时更新
- **Web Push**：浏览器系统通知
- **微信**：企业微信群机器人 Webhook
- **Telegram**：Bot API
- **邮件**：即时 / 每小时 / 每日摘要
- **免打扰**：可配置静默时段，重要博主可豁免
- **Cookie 过期提醒**：平台凭证失效时自动通知用户更新

### 其他
- **PWA 支持**：可添加到桌面，支持 Service Worker 缓存
- **Cookie 管理**：AES-256-GCM 加密存储平台凭证
- **开放 API**：API Key 认证（仅支持 `X-API-Key` Header），第三方客户端接入
- **健康监控**：适配器抓取成功率、耗时、错误追踪
- **国际化**：中文 / English

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + vue-i18n + DOMPurify |
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.0 |
| 任务调度 | Celery + Redis |
| 数据库 | PostgreSQL 16 |
| 爬虫 | httpx + BeautifulSoup + feedparser |
| RSS 代理 | RSSHub（自托管） |
| 安全 | defusedxml + slowapi 限流 + DOMPurify XSS 防护 |
| 部署 | Docker Compose（健康检查 + 自动迁移 + 日志轮转 + 非 root 容器） |

## 快速开始

### 前置条件

- Docker + Docker Compose
- Git

### 部署

```bash
# 1. 克隆项目
git clone https://github.com/rockbenben/juflow.git
cd juflow

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，必须修改：
#   - SECRET_KEY（改为随机字符串，否则启动时会警告）
#   - POSTGRES_PASSWORD（改为强密码）

# 3. 启动所有服务（带健康检查，自动等待依赖就绪，数据库迁移自动执行）
docker compose up -d

# 4. 访问
# 打开 http://localhost
# 注册后会看到推荐订阅源引导页，一键订阅即可开始
```

### 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 80 | Nginx 托管前端，反向代理 `/api`、`/ws`、`/docs`、`/health` 到后端 |
| backend | 8000 | FastAPI API + WebSocket（启动时自动执行数据库迁移） |
| celery-worker | — | 抓取 + 通知任务执行 |
| celery-beat | — | 定时调度 |
| postgres | — | 数据库（仅容器间通信，开发环境通过 override 暴露 5432） |
| redis | — | 任务队列 + 缓存（仅容器间通信，开发环境通过 override 暴露 6379） |
| rsshub | — | RSS 代理（开发环境通过 override 暴露 1200） |

> 开发端口通过 `docker-compose.override.yml` 暴露（compose 自动加载）。生产部署时删除此文件或指定 `docker compose -f docker-compose.yml up -d`。

## 使用指南

### 添加订阅

1. 登录后点击侧边栏底部的 **+ 添加订阅**
2. 粘贴博主主页 URL，如：
   - `https://xueqiu.com/u/1234567890`（雪球）
   - `https://blog.csdn.net/username`（CSDN）
   - `https://www.zhihu.com/people/someone`（知乎）
   - `半佛仙人`（微信公众号 — 直接输入名称）
3. 选择抓取频率，点击添加

### 配置通知

进入 **设置 → 通知**：
- 选择默认通知渠道
- 微信：填入企业微信群机器人 Webhook URL
- Telegram：填入 Bot Token 和 Chat ID
- 邮件：填入接收邮箱
- 配置免打扰时段

### 管理 Cookie

部分平台（集思录、淘股吧、小红书等）需要登录才能抓取内容：
1. 在浏览器中登录目标平台
2. 打开开发者工具（F12）→ Application → Cookies
3. 复制所有 Cookie 内容
4. 进入 **设置 → Cookie**，粘贴并保存

Cookie 使用 AES-256-GCM 加密存储。当 Cookie 过期时，系统会自动通过 WebSocket 推送提醒。

> **安全说明**：Cookie 在服务器端加密存储，但服务器管理员有能力解密。请仅在你信任的服务器上部署。

### 安装插件

社区开发的适配器插件可通过 **设置 → 插件** 安装（仅管理员，即第一个注册的用户）：
- 输入插件 Git 仓库 URL，点击安装
- 或上传 zip 包
- 安装后 API 端立即生效；后台抓取任务需重启 worker（`docker compose restart celery-worker`）

> **安全说明**：插件在服务器上执行 Python 代码。仅安装你信任的插件。

### API 接入

第三方客户端可通过 API Key 接入：
1. 进入 **设置 → API**，生成 API Key
2. 请求时携带 `X-API-Key` Header（不支持 URL 参数传递，防止密钥泄露到日志）
3. API 文档：`http://localhost/docs`

## 开发指南

### 本地开发

```bash
# 启动基础服务（override 文件自动暴露端口到 localhost）
docker compose up postgres redis rsshub -d

# 后端（不需要 .env，config.py 默认值指向 localhost）
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Celery Worker（新终端，在 backend/ 目录下）
celery -A app.tasks.celery_app worker --loglevel=info

# Celery Beat（新终端，在 backend/ 目录下）
celery -A app.tasks.celery_app beat --loglevel=info

# 前端（vite.config.ts 已配置 proxy，自动转发 /api /ws 到 localhost:8000）
cd frontend
npm install --legacy-peer-deps
npm run dev
```

> **注意**：`.env.example` 里的地址（`postgres`、`redis`）是 Docker 容器间通信用的。本地开发不要复制 `.env`，直接用 `config.py` 的默认值（`localhost`）即可。

### 编写适配器插件

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

### 项目结构

```
juflow/
├── backend/
│   ├── app/
│   │   ├── adapters/       # 平台适配器（3 个基类 + 14 个内置 + 插件加载）
│   │   ├── api/            # FastAPI 路由
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 验证模型
│   │   ├── services/       # 业务逻辑 + 通知渠道
│   │   ├── tasks/          # Celery 异步任务（共享数据库连接池）
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
│   │   ├── composables/    # 组合式函数（主题/快捷键/WebSocket/Toast）
│   │   ├── i18n/           # 国际化（zh-CN / en）
│   │   ├── stores/         # Pinia 状态管理
│   │   └── views/          # 页面视图
│   ├── Dockerfile          # 多阶段构建 + 健康检查
│   └── nginx.conf          # 反向代理 + gzip
├── postgres/
│   └── init.sql            # 数据库初始化脚本
├── plugins/adapters/       # 社区插件目录
├── docker-compose.yml      # 生产配置（无暴露 DB 端口）
├── docker-compose.override.yml  # 开发端口暴露（compose 自动加载）
├── .env.example
├── .gitattributes          # 强制 shell/Dockerfile LF 换行
└── README.md
```

## 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| `SECRET_KEY` | JWT 签名密钥（不设置会启动警告） | 是 |
| `POSTGRES_PASSWORD` | 数据库密码 | 是 |
| `DATABASE_URL` | 数据库连接字符串 | 是 |
| `REDIS_URL` | Redis 连接字符串 | 是 |
| `RSSHUB_URL` | RSSHub 实例地址 | 是 |
| `CORS_ORIGINS` | 允许的前端域名（逗号分隔） | 否（默认 localhost） |
| `VAPID_PRIVATE_KEY` | Web Push 私钥 | 否（Web Push 需要） |
| `VAPID_PUBLIC_KEY` | Web Push 公钥 | 否（Web Push 需要） |
| `SMTP_HOST` | 邮件服务器 | 否（邮件通知需要） |
| `SMTP_PORT` | 邮件端口 | 否 |
| `SMTP_USER` | 邮件账号 | 否 |
| `SMTP_PASSWORD` | 邮件密码 | 否 |
| `SMTP_FROM` | 发件人地址 | 否（默认 `noreply@juflow.app`） |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT 过期时间（分钟） | 否（默认 1440，即 24 小时） |
| `VAPID_CLAIM_EMAIL` | Web Push 联系邮箱 | 否（默认 `admin@example.com`） |

完整模板见 `.env.example`。

## 安全

- **XSS 防护**：文章内容通过 DOMPurify 净化，邮件/Telegram 通知内容 HTML 转义
- **XXE 防护**：OPML 导入使用 defusedxml
- **SSRF 防护**：订阅 URL 阻止内网/元数据地址
- **输入验证**：注册要求合法邮箱、密码 6 位以上、用户名 2-100 字符；搜索关键词转义 LIKE 通配符
- **认证限流**：登录 10 次/分钟，注册 5 次/分钟（slowapi）
- **插件隔离**：仅管理员可安装，插件名限制为字母数字，zip 防路径穿越
- **API Key 安全**：仅通过 Header 传递，不支持 URL 参数
- **Cookie 加密**：AES-256-GCM，按用户隔离

## 协议

MIT License
