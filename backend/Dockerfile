# Backend Dockerfile - 多阶段构建
# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# 安装 UV 包管理器
RUN pip install --no-cache-dir uv

# 复制依赖文件
COPY pyproject.toml ./

# 创建虚拟环境并安装依赖
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install -e .

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# 从 builder 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 复制应用代码
COPY src ./src

# 设置环境变量
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=2.0)" || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
