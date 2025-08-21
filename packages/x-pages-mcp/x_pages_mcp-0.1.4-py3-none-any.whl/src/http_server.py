#!/usr/bin/env python3
"""
X-Pages MCP HTTP Server

HTTP模式的独立启动器，通过环境变量配置。
"""

import argparse
import sys
from contextlib import asynccontextmanager

try:
    from dotenv import load_dotenv

    # 自动加载 .env 文件
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，继续运行
    pass

import uvicorn
from fastapi import FastAPI

try:
    # 尝试包模式导入
    from mcp_servers.xpages_mcp import get_config_from_env, mcp
except ImportError:
    # 尝试相对路径导入 (开发模式)
    try:
        from src.mcp_servers.xpages_mcp import get_config_from_env, mcp
    except ImportError:
        # 最后尝试直接导入
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from mcp_servers.xpages_mcp import get_config_from_env, mcp

# 导入版本信息
try:
    from src.version import get_version_info
except ImportError:
    try:
        from version import get_version_info
    except ImportError:
        def get_version_info():
            return {"version": "unknown", "python_version": "unknown", "platform": "unknown"}


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    """应用生命周期管理"""
    print("🚀 启动 X-Pages MCP HTTP 服务器...")
    yield
    print("👋 关闭 X-Pages MCP HTTP 服务器...")


# 创建MCP HTTP应用
mcp_app = mcp.http_app(path="/mcp")


# Combine lifespans
@asynccontextmanager
async def combined_lifespan(fastapi: FastAPI):
    """整合 fastmcp 必须整 结合 lifespan"""
    async with app_lifespan(fastapi):
        async with mcp_app.lifespan(fastapi):
            yield


# 创建主FastAPI应用
app = FastAPI(
    title="X-Pages MCP HTTP Server",
    description="HTTP模式的MCP服务器，用于HTML部署服务",
    version="1.0.0",
    lifespan=combined_lifespan,
)
app.mount("/llm", mcp_app)

# 挂载MCP应用


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "x-pages-mcp-http"}


@app.get("/")
async def root():
    """根路径信息"""
    return {
        "service": "X-Pages MCP HTTP Server",
        "mode": "HTTP",
        "mcp_endpoint": "/llm/mcp",
        "health_endpoint": "/health",
        "description": "HTTP模式使用环境变量配置：X_PAGES_BASE_URL, X_PAGES_API_TOKEN",
    }


def main():
    """HTTP模式启动入口"""
    parser = argparse.ArgumentParser(
        description="X-Pages MCP HTTP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
HTTP模式说明:
  HTTP模式也使用环境变量配置
  
必需环境变量:
  X_PAGES_BASE_URL      - X-Pages服务的基础URL
  X_PAGES_API_TOKEN     - API认证令牌

配置方法:
  1. 环境变量方式:
     export X_PAGES_BASE_URL=https://your-domain.com
     export X_PAGES_API_TOKEN=your-api-token

  2. .env文件方式:
     在项目根目录创建 .env 文件:
     X_PAGES_BASE_URL=https://your-domain.com
     X_PAGES_API_TOKEN=your-api-token

使用示例:
  %(prog)s                              # 启动在localhost:8083
  %(prog)s --host 0.0.0.0               # 监听所有接口
  %(prog)s --port 8080                  # 使用8080端口
  %(prog)s --host 0.0.0.0 --port 8080   # 监听所有接口的8080端口

API端点:
  GET  /                    - 服务信息
  GET  /health              - 健康检查
  POST /llm/mcp             - MCP API端点
        """,
    )

    parser.add_argument("--host", default="localhost", help="HTTP服务器主机地址 (默认: localhost)")
    parser.add_argument("--port", type=int, default=8083, help="HTTP服务器端口 (默认: 8083)")
    parser.add_argument("--reload", action="store_true", help="开发模式，文件变更时自动重载")

    args = parser.parse_args()

    version_info = get_version_info()
    
    print("=" * 60)
    print("🌐 X-Pages MCP HTTP Server")
    print("=" * 60)
    print(f"📦 版本: v{version_info['version']}")
    print(f"🐍 Python {version_info['python_version']} on {version_info['platform']}")
    print("📡 模式: HTTP")
    print(f"🔗 地址: http://{args.host}:{args.port}")
    print(f"🎯 MCP端点: http://{args.host}:{args.port}/llm/mcp")
    print(f"❤️  健康检查: http://{args.host}:{args.port}/health")
    print()
    print("📝 配置说明:")
    print("   HTTP模式使用环境变量配置")
    print("   必需环境变量: X_PAGES_BASE_URL, X_PAGES_API_TOKEN")

    # 检查环境变量
    try:
        config = get_config_from_env()
        print("✅ 配置已加载")
        print(f"🌐 目标服务: {config.base_url}")
        print(f"🔑 API Token: {'*' * (len(config.api_token) - 4)}{config.api_token[-4:]}")
    except ValueError as e:
        print(f"❌ 配置错误: {e}", file=sys.stderr)
        print("\n📝 请设置以下环境变量:", file=sys.stderr)
        print("   export X_PAGES_BASE_URL=https://your-domain.com", file=sys.stderr)
        print("   export X_PAGES_API_TOKEN=your-api-token", file=sys.stderr)
        print("\n💡 或创建 .env 文件:", file=sys.stderr)
        print("   X_PAGES_BASE_URL=https://your-domain.com", file=sys.stderr)
        print("   X_PAGES_API_TOKEN=your-api-token", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)

    try:
        if args.reload:
            # 在reload模式下，使用导入字符串
            uvicorn.run(
                "x_pages_mcp.http_server:app", host=args.host, port=args.port, reload=args.reload
            )
        else:
            # 在非reload模式下，直接使用app对象
            uvicorn.run(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n👋 HTTP服务器已停止")
    except Exception as e:
        print(f"\n❌ HTTP服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
