#!/usr/bin/env python3
"""
X-Pages MCP 统一入口点

支持通过 --mode 参数切换 STDIO 和 HTTP 模式
"""

import argparse
import sys
from typing import List

try:
    from dotenv import load_dotenv
    
    # 自动加载 .env 文件
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，继续运行
    pass

# 导入版本信息
try:
    from src.version import get_version_info
except ImportError:
    try:
        from version import get_version_info
    except ImportError:
        def get_version_info():
            return {"version": "unknown", "python_version": "unknown", "platform": "unknown"}


def main(args: List[str] = None) -> None:
    """统一入口点主函数"""
    parser = argparse.ArgumentParser(
        prog="x-pages-mcp",
        description="X-Pages MCP Server - 统一入口点",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
模式说明:
  stdio    - STDIO模式，用于Claude Desktop等本地客户端
  http     - HTTP模式，基于FastAPI的HTTP API服务

STDIO模式:
  使用标准输入输出进行通信，适用于Claude Desktop
  配置通过环境变量或.env文件提供
  
HTTP模式:  
  基于FastAPI的HTTP服务，默认端口8083
  同样使用环境变量配置
  支持开发模式 (--reload)

必需环境变量:
  X_PAGES_BASE_URL      - X-Pages服务的基础URL
  X_PAGES_API_TOKEN     - API认证令牌

使用示例:
  # STDIO模式
  x-pages-mcp stdio
  x-pages-mcp stdio --check-env
  
  # HTTP模式
  x-pages-mcp http
  x-pages-mcp http --port 8080
  x-pages-mcp http --host 0.0.0.0 --port 8083 --reload

Claude Desktop配置示例:
  {
    "mcpServers": {
      "x-pages-html-deployment": {
        "command": "uvx",
        "args": ["x-pages-mcp", "stdio"],
        "env": {
          "X_PAGES_BASE_URL": "https://your-domain.com",
          "X_PAGES_API_TOKEN": "your-secret-token"
        }
      }
    }
  }
        """,
    )

    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="mode", help="运行模式")

    # STDIO模式子命令
    stdio_parser = subparsers.add_parser(
        "stdio", 
        help="STDIO模式 - 用于Claude Desktop",
        description="STDIO模式通过标准输入输出进行通信"
    )
    stdio_parser.add_argument(
        "--check-env", 
        action="store_true", 
        help="只检查环境变量，不启动服务器"
    )

    # HTTP模式子命令  
    http_parser = subparsers.add_parser(
        "http",
        help="HTTP模式 - HTTP API服务",
        description="HTTP模式基于FastAPI提供HTTP API服务"
    )
    http_parser.add_argument(
        "--host", 
        default="localhost", 
        help="HTTP服务器主机地址 (默认: localhost)"
    )
    http_parser.add_argument(
        "--port", 
        type=int, 
        default=8083, 
        help="HTTP服务器端口 (默认: 8083)"
    )
    http_parser.add_argument(
        "--reload", 
        action="store_true", 
        help="开发模式，文件变更时自动重载"
    )

    # 解析参数
    parsed_args = parser.parse_args(args)
    
    # 确定运行模式
    mode = parsed_args.mode
    
    # 如果没有指定模式，默认为stdio（保持向后兼容）
    if not mode:
        mode = "stdio"
        print("⚠️  未指定模式，默认使用 STDIO 模式", file=sys.stderr)
        print("💡 提示：使用 'x-pages-mcp --help' 查看可用模式", file=sys.stderr)
    
    # 显示版本信息
    version_info = get_version_info()
    print(f"📦 X-Pages MCP v{version_info['version']}", file=sys.stderr)
    print(f"🐍 Python {version_info['python_version']} on {version_info['platform']}", file=sys.stderr)
    print(f"🚀 启动模式: {mode.upper()}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    # 根据模式启动对应服务
    try:
        if mode == "stdio":
            # 动态导入，支持不同的运行环境
            try:
                from src.stdio_server import main as stdio_main
            except ImportError:
                from stdio_server import main as stdio_main
            
            # 传递 stdio 特定的参数，重新构造 sys.argv
            if hasattr(parsed_args, 'check_env') and parsed_args.check_env:
                sys.argv = ["x-pages-mcp-stdio", "--check-env"]
            else:
                sys.argv = ["x-pages-mcp-stdio"]
                
            stdio_main()
            
        elif mode == "http":
            # 动态导入，支持不同的运行环境
            try:
                from src.http_server import main as http_main
            except ImportError:
                from http_server import main as http_main
            
            # 设置HTTP服务器的参数
            sys.argv = [
                "x-pages-mcp-http",
                "--host", parsed_args.host,
                "--port", str(parsed_args.port)
            ]
            if hasattr(parsed_args, 'reload') and parsed_args.reload:
                sys.argv.append("--reload")
                
            http_main()
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}", file=sys.stderr)
        print("💡 请确保在正确的环境中运行", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()