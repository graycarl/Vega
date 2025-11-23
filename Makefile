.PHONY: help setup up down restart logs test test-cov clean build

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## 显示此帮助信息
	@echo "$(GREEN)Vega Gateway - LLM API 网关系统$(NC)"
	@echo ""
	@echo "$(YELLOW)可用命令:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: ## 初始化开发环境（安装依赖）
	@echo "$(GREEN)初始化后端环境...$(NC)"
	cd backend && uv venv --clear
	cd backend && . .venv/bin/activate && uv pip install -e ".[dev]"
	@echo "$(GREEN)初始化前端环境...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ 环境初始化完成$(NC)"

up: ## 启动所有服务
	@echo "$(GREEN)启动服务...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ 服务已启动$(NC)"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:80"
	@echo "  Docs:     http://localhost:8000/docs"

down: ## 停止所有服务
	@echo "$(YELLOW)停止服务...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ 服务已停止$(NC)"

restart: down up ## 重启所有服务

logs: ## 查看服务日志
	docker-compose logs -f

logs-backend: ## 查看后端日志
	docker-compose logs -f backend

logs-frontend: ## 查看前端日志
	docker-compose logs -f frontend

test: ## 运行后端测试
	@echo "$(GREEN)运行测试...$(NC)"
	cd backend && . .venv/bin/activate && pytest

test-cov: ## 运行测试并生成覆盖率报告
	@echo "$(GREEN)运行测试并生成覆盖率报告...$(NC)"
	cd backend && . .venv/bin/activate && pytest --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ 覆盖率报告已生成: backend/htmlcov/index.html$(NC)"

lint: ## 运行代码质量检查
	@echo "$(GREEN)运行代码检查...$(NC)"
	cd backend && . .venv/bin/activate && black src tests && ruff check src tests && mypy src
	cd frontend && npm run lint
	@echo "$(GREEN)✓ 代码检查完成$(NC)"

build: ## 构建 Docker 镜像
	@echo "$(GREEN)构建 Docker 镜像...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ 镜像构建完成$(NC)"

clean: ## 清理临时文件和缓存
	@echo "$(YELLOW)清理临时文件...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf frontend/node_modules frontend/dist 2>/dev/null || true
	@echo "$(GREEN)✓ 清理完成$(NC)"

dev-backend: ## 本地开发模式运行后端（热重载）
	@echo "$(GREEN)启动后端开发服务器...$(NC)"
	cd backend && . .venv/bin/activate && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## 本地开发模式运行前端（热重载）
	@echo "$(GREEN)启动前端开发服务器...$(NC)"
	cd frontend && npm run dev

ps: ## 查看服务状态
	docker-compose ps

shell-backend: ## 进入后端容器 shell
	docker-compose exec backend /bin/bash

shell-frontend: ## 进入前端容器 shell
	docker-compose exec frontend /bin/sh
