# Implementation Plan: LLM API Gateway 网关系统

**Branch**: `001-api-gateway` | **Date**: 2025-11-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-api-gateway/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

构建一个 LLM API Gateway，提供统一的 OpenAI 格式 API 入口，支持请求代理、智能限流排队、配置管理和用量统计。技术栈采用 Python 3.12 + asyncio + FastAPI 实现高并发网关服务，Vue.js 构建 Admin Console 管理界面。

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI (异步 Web 框架), httpx (异步 HTTP 客户端), asyncio (并发处理), Vue.js 3 (前端框架), Pydantic (数据验证)  
**Storage**: SQLite (配置和统计数据持久化) - 初期使用 SQLite，后期可扩展为 PostgreSQL  
**Testing**: pytest + pytest-asyncio (异步测试支持), pytest-cov (覆盖率)  
**Target Platform**: Linux/macOS 服务器环境，Docker 容器化部署  
**Project Type**: Web 应用（Backend API + Frontend Console）  
**Performance Goals**: 支持 1000+ 并发请求，网关代理延迟 <50ms，配置变更 <5s 生效  
**Constraints**: 队列排队超时 30s，配置动态加载无需重启，用量统计准确率 99.9%  
**Scale/Scope**: 支持多后端服务器配置，按服务器维度限流，按服务器+应用维度统计

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 核心原则检查

- ✅ **测试驱动开发 (TDD)**: 将为所有功能编写测试（代理、限流、配置、统计）
- ✅ **中文优先文档**: 所有文档和注释使用中文
- ✅ **UV 环境管理**: 使用 UV 管理 Python 依赖，pyproject.toml 声明所有依赖
- ✅ **Docker 容器化**: 提供 Dockerfile 和 docker-compose.yml，支持多阶段构建
- ✅ **本地开发便利性**: 提供 Makefile 和 docker-compose 实现一键启动
- ✅ **可观测性**: 使用结构化 JSON 日志，记录关键操作和错误
- ✅ **集成测试**: 为网关代理、Admin Console API、限流排队提供集成测试

### 技术栈约束

- ✅ **Python 3.12**: 满足 3.11+ 要求，使用类型提示
- ✅ **pytest**: 作为测试框架，配合 pytest-asyncio 和 pytest-cov
- ✅ **Docker**: 使用官方 Python slim 镜像，多阶段构建
- ✅ **Makefile + docker-compose**: 提供任务自动化和本地服务编排

**结论**: 无违反章程原则，可以进入 Phase 0 研究

## Project Structure

### Documentation (this feature)

```text
specs/001-api-gateway/
├── plan.md              # 本文件 (实现计划)
├── spec.md              # 功能规格说明
├── research.md          # Phase 0: 技术调研输出
├── data-model.md        # Phase 1: 数据模型设计
├── quickstart.md        # Phase 1: 快速开始指南
├── contracts/           # Phase 1: API 契约定义
│   ├── gateway-api.yaml    # 网关代理 API (OpenAPI 格式)
│   └── admin-api.yaml      # Admin Console API (OpenAPI 格式)
└── tasks.md             # Phase 2: 任务分解 (由 /speckit.tasks 生成)
```

### Source Code (repository root)

```text
vega-gateway/                    # 项目根目录
├── backend/                     # FastAPI 后端服务
│   ├── src/
│   │   ├── gateway/            # 网关核心模块
│   │   │   ├── proxy.py        # LLM 请求代理
│   │   │   ├── rate_limiter.py # 限流逻辑
│   │   │   └── queue.py        # 请求队列管理
│   │   ├── admin/              # Admin Console API
│   │   │   ├── config.py       # 服务器配置管理
│   │   │   └── stats.py        # 用量统计
│   │   ├── models/             # 数据模型
│   │   │   ├── server_config.py   # 后端服务器配置
│   │   │   ├── request_log.py     # 请求记录
│   │   │   └── usage_stats.py     # 用量统计
│   │   ├── storage/            # 数据持久化
│   │   │   └── database.py     # SQLite/数据库操作
│   │   ├── api/                # API 路由
│   │   │   ├── gateway_routes.py  # 网关路由 (代理请求)
│   │   │   └── admin_routes.py    # Admin API 路由
│   │   ├── config.py           # 应用配置
│   │   └── main.py             # FastAPI 应用入口
│   ├── tests/
│   │   ├── contract/           # 契约测试 (OpenAPI 合规性)
│   │   ├── integration/        # 集成测试
│   │   │   ├── test_proxy.py      # 代理功能测试
│   │   │   ├── test_rate_limit.py # 限流排队测试
│   │   │   └── test_admin.py      # Admin API 测试
│   │   └── unit/               # 单元测试
│   │       ├── test_queue.py      # 队列逻辑测试
│   │       └── test_models.py     # 数据模型测试
│   ├── pyproject.toml          # UV 依赖配置
│   └── Dockerfile              # 后端 Docker 镜像
│
├── frontend/                    # Vue.js 前端
│   ├── src/
│   │   ├── components/         # Vue 组件
│   │   │   ├── ServerConfig.vue   # 服务器配置组件
│   │   │   └── UsageStats.vue     # 用量统计组件
│   │   ├── pages/              # 页面
│   │   │   ├── Dashboard.vue      # 仪表盘
│   │   │   └── Servers.vue        # 服务器管理
│   │   ├── services/           # API 服务
│   │   │   └── api.js          # 后端 API 调用
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 前端入口
│   ├── tests/
│   │   └── unit/               # 前端单元测试
│   ├── package.json            # npm 依赖
│   ├── vite.config.js          # Vite 构建配置
│   └── Dockerfile              # 前端 Docker 镜像 (nginx)
│
├── docker-compose.yml           # 本地开发环境编排
├── Makefile                     # 任务自动化
└── README.md                    # 项目说明文档
```

**Structure Decision**: 采用 Web 应用结构（Option 2），前后端分离。Backend 使用 FastAPI 提供网关代理和 Admin API，Frontend 使用 Vue.js 构建 Admin Console。两者通过 docker-compose 协同工作，Makefile 提供统一命令入口。

## Complexity Tracking

> 无需填写 - 本项目未违反章程原则
