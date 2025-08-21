#!/usr/bin/env python3
"""
X-Pages MCP STDIO Server

STDIO模式的独立启动器，用于Claude Desktop等客户端。
"""

import argparse
import os
import sys

try:
    from dotenv import load_dotenv

    # 自动加载 .env 文件
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，继续运行
    pass

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


def check_environment() -> bool:
    """检查必要的环境变量"""
    required_vars = ["X_PAGES_BASE_URL", "X_PAGES_API_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ 缺少必要的环境变量:", file=sys.stderr)
        for var in missing_vars:
            print(f"   {var}", file=sys.stderr)
        print("\n📝 请设置环境变量:", file=sys.stderr)
        print("   export X_PAGES_BASE_URL=https://your-domain.com", file=sys.stderr)
        print("   export X_PAGES_API_TOKEN=your-api-token", file=sys.stderr)
        print("\n💡 或创建 .env 文件:", file=sys.stderr)
        print("   X_PAGES_BASE_URL=https://your-domain.com", file=sys.stderr)
        print("   X_PAGES_API_TOKEN=your-api-token", file=sys.stderr)
        return False

    return True


def main():
    """STDIO模式启动入口"""
    parser = argparse.ArgumentParser(
        description="X-Pages MCP STDIO Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
STDIO模式说明:
  使用标准输入输出进行通信，适用于Claude Desktop等客户端
  配置通过环境变量提供
  
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

Claude Desktop配置示例:
  {
    "mcpServers": {
      "x-pages-html-deployment": {
        "command": "uv",
        "args": ["run", "x-pages-mcp-stdio"],
        "env": {
          "X_PAGES_BASE_URL": "https://your-domain.com",
          "X_PAGES_API_TOKEN": "your-secret-token"
        }
      }
    }
  }
        """,
    )

    parser.add_argument("--check-env", action="store_true", help="只检查环境变量，不启动服务器")

    args = parser.parse_args()

    # 检查环境变量
    if not check_environment():
        sys.exit(1)

    if args.check_env:
        version_info = get_version_info()
        print(f"📦 X-Pages MCP v{version_info['version']}")
        print("✅ 环境变量检查通过")
        return

    try:
        config = get_config_from_env()
        version_info = get_version_info()
        
        print("=" * 50, file=sys.stderr)
        print("📡 X-Pages MCP STDIO Server", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print(f"📦 版本: v{version_info['version']}", file=sys.stderr)
        print(f"🐍 Python {version_info['python_version']} on {version_info['platform']}", file=sys.stderr)
        print("✅ 配置已加载", file=sys.stderr)
        print(f"🌐 目标服务: {config.base_url}", file=sys.stderr)
        print(
            f"🔑 API Token: {'*' * (len(config.api_token) - 4)}{config.api_token[-4:]}",
            file=sys.stderr,
        )
        print("📡 传输模式: STDIO", file=sys.stderr)
        print("🚀 MCP服务器启动中...", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
    except ValueError as e:
        print(f"❌ 配置错误: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # 启动STDIO模式
        mcp.run(transport="stdio")

    except KeyboardInterrupt:
        print("\n👋 STDIO服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"\n❌ STDIO服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
