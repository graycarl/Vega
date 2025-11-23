# Vega Gateway - LLM API 网关系统

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

统一的 LLM API 网关，提供请求代理、智能限流排队、配置管理和用量统计功能。

## 功能特性

- **🔀 OpenAI 兼容代理**: 完全兼容 OpenAI API 格式，无缝接入多个 LLM 后端服务
- **⏱️ 智能限流排队**: RPM/TPM 双维度限流，超限请求自动排队而非拒绝
- **⚙️ 动态配置管理**: 支持多后端服务器配置，5 秒内热加载无需重启
- **📊 用量统计分析**: 按服务器+应用维度统计请求数和 token 使用量
- **🎨 Web 管理控制台**: Vue.js 构建的直观管理界面

## 技术栈

**后端**:
- Python 3.12 + FastAPI (异步 Web 框架)
- httpx (异步 HTTP 客户端)
- aiosqlite (异步 SQLite 数据库)
- Pydantic (数据验证)
- structlog (结构化日志)

**前端**:
- Vue.js 3 (渐进式框架)
- Vite (构建工具)
- Chart.js (数据可视化)
- Axios (HTTP 客户端)

**部署**:
- Docker + docker-compose (容器化)
- UV (Python 包管理)
- Makefile (任务自动化)

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Make (可选，用于快捷命令)

### 一键启动

```bash
# 克隆仓库
git clone https://github.com/graycarl/vega.git
cd vega

# 使用 Make 启动（推荐）
make setup  # 初始化环境
make up     # 启动服务

# 或直接使用 docker-compose
docker-compose up -d
```

### 访问服务

- **API 网关**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **管理控制台**: http://localhost:80

### 本地开发

```bash
# 后端开发（热重载）
make dev-backend

# 前端开发（热重载）
make dev-frontend

# 运行测试
make test

# 代码质量检查
make lint
```

## 项目结构

```
vega-gateway/
├── backend/                    # FastAPI 后端
│   ├── src/
│   │   ├── gateway/           # 网关核心（代理、限流、队列）
│   │   ├── admin/             # Admin API（配置、统计）
│   │   ├── models/            # 数据模型
│   │   ├── storage/           # 数据持久化
│   │   ├── api/               # API 路由
│   │   └── main.py            # 应用入口
│   ├── tests/                 # 测试套件
│   ├── pyproject.toml         # Python 依赖
│   └── Dockerfile             # 后端镜像
│
├── frontend/                   # Vue.js 前端
│   ├── src/
│   │   ├── components/        # Vue 组件
│   │   ├── pages/             # 页面
│   │   ├── services/          # API 服务
│   │   └── main.js            # 前端入口
│   ├── package.json           # npm 依赖
│   ├── Dockerfile             # 前端镜像
│   └── nginx.conf             # nginx 配置
│
├── docs/                       # 文档
├── docker-compose.yml          # 服务编排
├── Makefile                    # 任务自动化
└── README.md                   # 本文件
```

## 使用指南

### 配置后端 LLM 服务器

1. 访问管理控制台: http://localhost
2. 进入"服务器管理"页面
3. 添加新服务器，填写：
   - 服务器名称
   - API 基础 URL（如 `https://api.openai.com/v1`）
   - API Key
   - 支持的模型列表（如 `["gpt-4", "gpt-3.5-turbo"]`）
   - RPM 限流（每分钟请求数）
   - TPM 限流（每分钟 token 数）

### 调用网关 API

```bash
# 示例：调用 GPT-4
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "App-Name: my-chatbot" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**注意**: 必须在请求头中包含 `App-Name` 字段标识客户端身份。

### 查看用量统计

1. 访问管理控制台首页（仪表盘）
2. 查看按服务器+应用维度的用量图表
3. 可按时间范围筛选（今日/本周/本月）
4. 导出 CSV 报表进行深度分析

## 开发指南

### 运行测试

```bash
# 单元测试
make test

# 测试覆盖率报告
make test-cov

# 查看覆盖率: backend/htmlcov/index.html
```

### 代码规范

项目遵循 [Vega 项目章程](https://github.com/graycarl/vega/blob/main/.specify/memory/constitution.md)：

- ✅ **TDD 开发**: 先写测试，再写代码
- ✅ **中文文档**: 所有文档和注释使用中文
- ✅ **UV 环境管理**: 使用 UV 管理 Python 依赖
- ✅ **Docker 容器化**: 多阶段构建优化镜像体积
- ✅ **结构化日志**: 使用 JSON 格式记录日志

### Make 命令速查

```bash
make help          # 显示所有可用命令
make setup         # 初始化开发环境
make up            # 启动服务
make down          # 停止服务
make logs          # 查看日志
make test          # 运行测试
make test-cov      # 测试覆盖率
make lint          # 代码检查
make clean         # 清理临时文件
```

## 性能指标

- **并发支持**: 1000+ 并发客户端请求
- **代理延迟**: < 50ms 额外延迟
- **配置生效**: < 5 秒热加载
- **统计准确率**: ≥ 99.9%
- **系统可用性**: ≥ 99.5% (月度)

## 架构设计

详细架构和技术决策文档:

- [功能规格](specs/001-api-gateway/spec.md)
- [实现计划](specs/001-api-gateway/plan.md)
- [技术调研](specs/001-api-gateway/research.md)
- [数据模型](specs/001-api-gateway/data-model.md)
- [任务分解](specs/001-api-gateway/tasks.md)

## 贡献指南

欢迎贡献代码！请遵循以下流程：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交变更 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

确保代码通过所有测试和质量检查:

```bash
make test && make lint
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- **项目主页**: https://github.com/graycarl/vega
- **问题反馈**: https://github.com/graycarl/vega/issues
- **维护团队**: Vega Team

---

**版本**: 0.1.0  
**最后更新**: 2025-11-23
