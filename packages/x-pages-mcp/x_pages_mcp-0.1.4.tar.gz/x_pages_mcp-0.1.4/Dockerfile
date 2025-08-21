# X-Pages MCP HTTP Server Docker Image
FROM python:3.11.13-bullseye

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src/ ./src/

# 安装依赖
RUN uv sync --no-dev

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# 创建缓存目录并设置权限
RUN mkdir -p /home/appuser/.cache/uv

# 暴露端口
EXPOSE 8083

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8083/health || exit 1

# 启动命令
CMD ["uv", "run", "x-pages-mcp-http", "--host", "0.0.0.0", "--port", "8083"]