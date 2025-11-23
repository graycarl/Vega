<!--
Sync Impact Report:
================================================================================
Version Change: [NEW] → 1.0.0
Modified Principles: Initial constitution creation
Added Sections: All (initial version)
Removed Sections: None
Templates Status:
  ✅ plan-template.md - Reviewed, compatible with constitution principles
  ✅ spec-template.md - Reviewed, compatible with constitution principles
  ✅ tasks-template.md - Reviewed, compatible with constitution principles
  ⚠️ checklist-template.md - Not reviewed (not critical for core workflow)
  ⚠️ agent-file-template.md - Not reviewed (not critical for core workflow)
Follow-up TODOs: None
Rationale: MINOR version (1.0.0) - Initial constitution establishing governance framework
================================================================================
-->

# Vega 项目章程
## 核心原则

### I. 测试驱动开发（强制性）
所有功能必须遵循测试驱动开发（TDD）流程：
- 先编写测试用例，经用户批准后，确认测试失败，然后才能开始实现
- 严格执行红-绿-重构循环
- 每个功能、每个库、每个服务都必须有对应的测试代码
- 没有测试的代码不允许合并到主分支

**理由**：测试先行确保代码质量，防止回归，提供可执行的功能规格文档。

### II. 中文优先文档
项目文档和代码注释优先使用中文：
- 所有 README、规格说明、用户文档必须使用中文
- 代码注释、函数文档字符串（docstring）使用中文
- 提交信息（commit message）可使用中文或英文
- 代码中的变量名、函数名、类名使用英文（遵循 Python 命名规范）

**理由**：降低团队沟通成本，提高文档可读性和可维护性。

### III. UV 环境管理
使用 UV 工具统一管理 Python 项目环境：
- 所有依赖必须在 `pyproject.toml` 中声明
- 使用 `uv` 进行包安装和虚拟环境管理
- 不使用 `pip` 或 `poetry` 等其他工具
- 提供清晰的环境设置文档

**理由**：UV 提供快速、可靠的依赖解析和环境管理，统一工具链简化开发流程。

### IV. Docker 容器化部署
程序必须打包为 Docker 镜像：
- 每个项目提供 `Dockerfile` 和 `.dockerignore`
- 使用 entrypoint 脚本区分不同服务（如 API、Worker、CLI 等）
- 镜像必须优化大小，使用多阶段构建
- 提供健康检查（health check）配置

**理由**：容器化确保环境一致性，简化部署和扩展。

### V. 本地开发便利性
使用 Makefile 和 docker-compose 提供快速本地测试：
- `Makefile` 提供常用命令快捷方式（如 `make test`、`make run`、`make build`）
- `docker-compose.yml` 定义完整的本地开发环境（包括数据库、缓存等依赖服务）
- 一条命令即可启动完整的开发环境
- 提供 `make help` 显示所有可用命令

**理由**：降低新开发者上手门槛，标准化本地开发流程。

### VI. 可观测性
所有服务必须具备可观测性：
- 使用结构化日志（JSON 格式）
- 记录关键操作、错误和性能指标
- 日志级别可配置（DEBUG、INFO、WARNING、ERROR）
- 敏感信息不得出现在日志中

**理由**：可观测性是生产环境问题诊断和性能优化的基础。

### VII. 集成测试
关键集成点必须有集成测试覆盖：
- 新的服务契约（API 接口）
- 服务间通信
- 数据库交互
- 第三方服务集成
- 共享数据模式（schema）变更

**理由**：集成测试确保各组件协同工作，提前发现集成问题。

## 技术栈约束

### Python 版本
- Python 3.11 或更高版本
- 使用类型提示（type hints）
- 遵循 PEP 8 代码风格

### 测试框架
- 使用 `pytest` 作为测试框架
- 使用 `pytest-cov` 生成覆盖率报告
- 使用 `pytest-asyncio` 测试异步代码（如需要）

### 容器化
- 基础镜像使用官方 Python slim 镜像
- 多阶段构建减小镜像体积
- 使用 `.dockerignore` 排除不必要文件

### 本地开发工具
- `Makefile` 提供任务自动化
- `docker-compose` 管理本地服务编排
- UV 管理 Python 依赖

## 开发工作流

### 功能开发流程
1. 创建功能规格文档（使用 `/speckit.specify` 命令）
2. 编写测试用例（先写测试，确认失败）
3. 实现功能代码（通过测试）
4. 重构优化（保持测试通过）
5. 更新文档（中文文档）
6. 提交代码审查

### 代码审查要求
- 所有代码必须经过审查才能合并
- 审查检查项：
  - 是否有对应的测试代码
  - 测试是否覆盖主要场景和边界情况
  - 代码是否有中文注释
  - 是否符合项目架构原则
  - Docker 镜像是否可构建

### 质量门禁
合并前必须满足：
- 所有测试通过
- 代码覆盖率不降低
- Docker 镜像构建成功
- 通过代码审查

## 治理规则

本章程优先于所有其他开发实践和规范。

### 修订流程
章程修订需要：
1. 提出修订建议并说明理由
2. 评估对现有代码和流程的影响
3. 更新相关模板和文档
4. 记录修订历史

### 版本管理
章程使用语义化版本号（MAJOR.MINOR.PATCH）：
- **MAJOR**：不兼容的原则移除或重新定义
- **MINOR**：新增原则或章节
- **PATCH**：文字澄清、措辞优化、错别字修正

### 合规审查
- 所有 PR 必须验证章程合规性
- 违反核心原则的代码不予合并
- 如需违反原则必须提供充分理由并记录在案

**版本**: 1.0.0 | **批准日期**: 2025-11-23 | **最后修订**: 2025-11-23
