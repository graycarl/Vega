# 快速开始指南 - LLM API Gateway

本指南帮助开发者快速搭建本地开发环境并启动 LLM API Gateway 项目。

## 前置要求

- **Python**: 3.12+
- **UV**: 最新版本（用于 Python 依赖管理）
- **Docker**: 20.10+ 和 Docker Compose v2+
- **Node.js**: 18+ 和 npm 9+（用于前端开发）
- **Make**: 用于任务自动化

### 安装工具

```bash
# macOS
brew install uv docker node make

# Linux (Ubuntu/Debian)
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo apt-get install docker.io docker-compose-v2 nodejs npm make

# 验证安装
uv --version
docker --version
node --version
make --version
```

---

## 项目结构

```text
vega-gateway/
├── backend/           # FastAPI 后端
├── frontend/          # Vue.js 前端
├── docker-compose.yml # 本地环境编排
├── Makefile           # 任务快捷命令
└── README.md          # 项目说明
```

---

## 一键启动（推荐）

使用 Makefile 提供的命令快速启动完整开发环境：

```bash
# 克隆项目（假设已创建）
git clone <repository-url> vega-gateway
cd vega-gateway

# 查看所有可用命令
make help

# 初始化环境（首次运行）
make setup

# 启动所有服务（后端 + 前端 + 数据库）
make up

# 查看服务日志
make logs

# 停止所有服务
make down
```

服务启动后，访问：
- **Admin Console**: http://localhost:5173
- **Gateway API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 分步启动（手动）

### 1. 后端开发环境

#### 安装依赖

```bash
cd backend

# 使用 UV 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装项目依赖
uv pip install -e .
```

#### 初始化数据库

```bash
# 运行数据库迁移脚本（首次启动）
python -m src.storage.init_db

# 确认数据库文件创建
ls gateway.db
```

#### 启动后端服务

```bash
# 开发模式（自动重载）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Makefile
make backend-dev
```

后端服务启动在 http://localhost:8000

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/integration/test_proxy.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
open htmlcov/index.html  # 查看覆盖率报告
```

---

### 2. 前端开发环境

#### 安装依赖

```bash
cd frontend

# 安装 npm 依赖
npm install
```

#### 启动前端开发服务器

```bash
# 开发模式（热重载）
npm run dev

# 或使用 Makefile
make frontend-dev
```

前端服务启动在 http://localhost:5173

Vite 会自动代理 API 请求到后端（配置在 `vite.config.js`）。

#### 构建生产版本

```bash
# 构建静态文件到 dist/
npm run build

# 预览生产构建
npm run preview
```

---

### 3. 使用 Docker Compose（推荐）

Docker Compose 可以一次启动所有服务，包括后端、前端和数据库。

#### 启动服务

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### 停止服务

```bash
# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

#### 服务端口

- Backend API: http://localhost:8000
- Frontend: http://localhost:8080 (生产模式，nginx 服务)
- Admin Console (开发): http://localhost:5173

---

## 配置说明

### 后端配置

后端配置通过环境变量或 `.env` 文件设置：

```bash
# backend/.env
DATABASE_URL=sqlite:///./gateway.db
LOG_LEVEL=INFO
CONFIG_RELOAD_INTERVAL=5  # 配置重新加载间隔（秒）
MAX_QUEUE_SIZE=100        # 默认队列大小
QUEUE_TIMEOUT=30          # 默认队列超时（秒）
```

### 前端配置

前端通过 Vite 环境变量配置（`frontend/.env`）：

```bash
# 开发环境
VITE_API_BASE_URL=http://localhost:8000/api

# 生产环境
VITE_API_BASE_URL=https://gateway.example.com/api
```

---

## 开发工作流

### 1. 添加新功能

遵循测试驱动开发（TDD）流程：

```bash
# 1. 先写测试
vim tests/unit/test_new_feature.py

# 2. 运行测试（应该失败）
pytest tests/unit/test_new_feature.py

# 3. 实现功能
vim src/new_feature.py

# 4. 再次运行测试（应该通过）
pytest tests/unit/test_new_feature.py

# 5. 重构并确保测试仍然通过
pytest
```

### 2. 代码格式化

```bash
# 使用 black 格式化代码
cd backend
uv pip install black
black src/ tests/

# 使用 ruff 检查代码质量
uv pip install ruff
ruff check src/
```

### 3. 类型检查

```bash
# 使用 mypy 进行类型检查
cd backend
uv pip install mypy
mypy src/
```

---

## 常见任务

### 添加新的后端服务器配置

使用 Admin Console 或直接调用 API：

```bash
curl -X POST http://localhost:8000/api/servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpenAI GPT-4",
    "url": "https://api.openai.com/v1",
    "api_key": "sk-xxxxxxxxxxxxxxxx",
    "models": ["gpt-4", "gpt-3.5-turbo"],
    "rpm_limit": 60,
    "tpm_limit": 90000
  }'
```

### 通过网关发送请求

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "App-Name: my-chatbot" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
  }'
```

### 查看用量统计

```bash
# 获取今天的用量统计
curl "http://localhost:8000/api/stats?start_time=2025-11-23T00:00:00Z&end_time=2025-11-23T23:59:59Z&bucket_type=hour"
```

---

## 故障排查

### 后端服务无法启动

1. 检查 Python 版本：`python --version`（应为 3.12+）
2. 检查依赖是否安装：`uv pip list`
3. 查看日志：`docker-compose logs backend`

### 前端无法连接后端

1. 确认后端服务正在运行：`curl http://localhost:8000/health`
2. 检查 CORS 配置（开发模式下应自动允许）
3. 检查 `vite.config.js` 中的代理配置

### 数据库错误

1. 删除旧数据库：`rm backend/gateway.db`
2. 重新初始化：`python -m src.storage.init_db`
3. 重启服务：`make restart`

---

## Makefile 命令参考

```bash
make help              # 显示所有可用命令
make setup             # 初始化开发环境
make up                # 启动所有服务
make down              # 停止所有服务
make restart           # 重启所有服务
make logs              # 查看所有服务日志
make test              # 运行所有测试
make test-cov          # 运行测试并生成覆盖率报告
make lint              # 运行代码检查
make format            # 格式化代码
make build             # 构建 Docker 镜像
make clean             # 清理临时文件和缓存
```

---

## 下一步

- 阅读 [API 契约文档](./contracts/) 了解完整 API 规范
- 查看 [数据模型设计](./data-model.md) 了解数据结构
- 参考 [实现计划](./plan.md) 了解技术架构

---

## 需要帮助？

- 查看项目 README.md
- 查看 `/docs` 的 API 自动文档
- 提交 Issue 或 Pull Request
