"""版本信息模块"""

import sys
from pathlib import Path

def get_version() -> str:
    """获取包版本信息"""
    try:
        # 优先尝试从已安装的包获取版本
        try:
            import importlib.metadata
            return importlib.metadata.version("x-pages-mcp")
        except importlib.metadata.PackageNotFoundError:
            pass
        except ImportError:
            # Python < 3.8 fallback
            try:
                import pkg_resources
                return pkg_resources.get_distribution("x-pages-mcp").version
            except Exception:
                pass
        
        # 如果包未安装，从 pyproject.toml 读取版本
        try:
            import tomllib
            
            # 查找 pyproject.toml 文件
            current_dir = Path(__file__).parent
            for _ in range(5):  # 最多向上查找5级目录
                pyproject_file = current_dir / "pyproject.toml"
                if pyproject_file.exists():
                    with open(pyproject_file, "rb") as f:
                        data = tomllib.load(f)
                        return data.get("project", {}).get("version", "unknown")
                current_dir = current_dir.parent
        except Exception:
            pass
        
        # 最后的回退方案
        return "dev"
        
    except Exception:
        return "unknown"


def get_version_info() -> dict:
    """获取完整的版本和环境信息"""
    return {
        "version": get_version(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
    }


if __name__ == "__main__":
    info = get_version_info()
    print(f"X-Pages MCP v{info['version']}")
    print(f"Python {info['python_version']} on {info['platform']}")