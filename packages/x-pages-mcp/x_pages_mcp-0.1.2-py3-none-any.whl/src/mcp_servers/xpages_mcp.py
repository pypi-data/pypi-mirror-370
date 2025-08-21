"""X-Pages MCP工具函数和配置管理."""

import os
import secrets
from pathlib import Path
from urllib.parse import urljoin

import httpx
import markdown
from fastmcp import FastMCP
from pydantic import AnyHttpUrl, BaseModel, Field


class XPagesConfig(BaseModel):
    """Configuration for X-Pages service."""

    base_url: AnyHttpUrl = Field(
        description="Base URL of the X-Pages service",
        examples=["https://your-domain.com", "http://localhost:3000"],
    )
    api_token: str = Field(description="API token for X-Pages authentication (x-token)")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")


class DeployResult(BaseModel):
    """Result from HTML deployment."""

    success: bool
    site_name: str
    deploy_url: str
    deployed_at: str
    content_length: int
    message: str


class DeleteResult(BaseModel):
    """Result from HTML deletion."""

    success: bool
    site_name: str
    deleted_at: str
    message: str


def get_config_from_env() -> XPagesConfig:
    """Get configuration from environment variables."""
    base_url = os.getenv("X_PAGES_BASE_URL")
    api_token = os.getenv("X_PAGES_API_TOKEN")

    if not base_url:
        raise ValueError(
            "X_PAGES_BASE_URL environment variable is required. Example: https://your-domain.com"
        )

    if not api_token:
        raise ValueError(
            "X_PAGES_API_TOKEN environment variable is required. "
            "This is your x-token for API authentication."
        )

    return XPagesConfig(base_url=base_url, api_token=api_token, timeout=30.0)


def get_config() -> XPagesConfig:
    """Get configuration from environment variables."""
    return get_config_from_env()


def generate_site_name() -> str:
    """Generate a 24-character unique site name using hex characters."""
    return secrets.token_hex(12)  # 12 bytes = 24 hex characters


def detect_file_type(file_path: Path) -> str:
    """检测文件类型基于扩展名."""
    suffix = file_path.suffix.lower()

    if suffix in [".html", ".htm"]:
        return "html"
    if suffix in [".md", ".markdown"]:
        return "markdown"
    if suffix in [".txt"]:
        return "text"
    return "unknown"


def convert_text_to_html(content: str, file_type: str, title: str | None = None) -> str:
    """将不同格式的文本内容转换为HTML."""

    if file_type == "html":
        return content

    if file_type == "markdown":
        # 转换Markdown到HTML
        html_content = markdown.markdown(
            content,
            extensions=["extra", "codehilite", "toc"],
            extension_configs={"codehilite": {"css_class": "highlight", "use_pygments": False}},
        )

        # 包装成完整的HTML文档
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or "Markdown Document"}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            color: #333;
        }}
        code {{ 
            background-color: #f5f5f5; 
            padding: 2px 4px; 
            border-radius: 3px; 
            font-family: 'Monaco', 'Courier New', monospace;
        }}
        pre {{ 
            background-color: #f5f5f5; 
            padding: 10px; 
            border-radius: 5px; 
            overflow-x: auto;
        }}
        blockquote {{ 
            border-left: 4px solid #ddd; 
            margin: 0; 
            padding-left: 20px; 
            color: #666;
        }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }}
        th {{ 
            background-color: #f2f2f2; 
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    if file_type == "text":
        # 转换纯文本为HTML，保持换行和空格
        escaped_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        formatted_content = escaped_content.replace("\n", "<br>")

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or "Text Document"}</title>
    <style>
        body {{ 
            font-family: 'Monaco', 'Courier New', monospace;
            line-height: 1.6; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            color: #333;
            background-color: #f9f9f9;
        }}
        pre {{ 
            white-space: pre-wrap; 
            word-wrap: break-word; 
        }}
    </style>
</head>
<body>
    <pre>{formatted_content}</pre>
</body>
</html>"""

    else:
        raise ValueError(f"不支持的文件类型: {file_type}")


async def _deploy_html_content(html_content: str) -> DeployResult:
    """
    内部函数：部署HTML内容到X-Pages服务的核心逻辑。

    Args:
        html_content: 完整的HTML内容

    Returns:
        部署结果，包含访问URL和部署信息
    """
    config = get_config()

    # 生成24位随机唯一站点名称
    site_name = generate_site_name()

    # 构建部署URL
    deploy_url = urljoin(str(config.base_url), "/html/deploy")

    # 准备请求头
    headers = {
        "Content-Type": "text/html; charset=utf-8",
        "x-token": config.api_token,
        "htmlkey": site_name,
    }

    # 发送部署请求
    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            response = await client.post(
                deploy_url, content=html_content.encode("utf-8"), headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                return DeployResult(
                    success=data["success"],
                    site_name=data["data"]["siteName"],
                    deploy_url=urljoin(str(config.base_url), data["data"]["deployUrl"]),
                    deployed_at=data["data"]["deployedAt"],
                    content_length=data["data"]["contentLength"],
                    message=data["message"],
                )

            error_data = (
                response.json()
                if response.headers.get("content-type", "").startswith("application/json")
                else {}
            )
            error_msg = error_data.get("error", f"HTTP {response.status_code}")
            raise ValueError(f"部署失败: {error_msg}")

        except httpx.TimeoutException as exc:
            raise ValueError(f"请求超时 ({config.timeout}秒)") from exc
        except httpx.RequestError as exc:
            raise ValueError(f"网络请求失败: {exc!s}") from exc


# 创建MCP服务器实例
mcp = FastMCP("X-Pages HTML Deployment")


@mcp.tool()
async def deploy_html(html_content: str) -> DeployResult:
    """
    部署HTML内容到X-Pages服务。

    Args:
        html_content: 完整的HTML内容

    Returns:
        部署结果，包含访问URL和部署信息（site_name为自动生成的24位唯一标识符）
    """
    return await _deploy_html_content(html_content)


@mcp.tool()
async def delete_html(site_name: str) -> DeleteResult:
    """
    从X-Pages服务删除HTML站点。

    Args:
        site_name: 要删除的站点名称

    Returns:
        删除结果信息
    """
    config = get_config()

    # 构建删除URL
    delete_url = urljoin(str(config.base_url), f"/html/delete?siteName={site_name}")

    # 准备请求头
    headers = {"x-token": config.api_token}

    # 发送删除请求
    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            response = await client.delete(delete_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return DeleteResult(
                    success=data["success"],
                    site_name=data["data"]["siteName"],
                    deleted_at=data["data"]["deletedAt"],
                    message=data["message"],
                )

            error_data = (
                response.json()
                if response.headers.get("content-type", "").startswith("application/json")
                else {}
            )
            error_msg = error_data.get("error", f"HTTP {response.status_code}")
            raise ValueError(f"删除失败: {error_msg}")

        except httpx.TimeoutException as exc:
            raise ValueError(f"请求超时 ({config.timeout}秒)") from exc
        except httpx.RequestError as exc:
            raise ValueError(f"网络请求失败: {exc!s}") from exc


@mcp.tool()
async def deploy_file(file_path: str) -> DeployResult:
    """
    部署本地文件到X-Pages服务，支持HTML、Markdown、TXT等格式。

    支持的文件格式：
    - HTML文件 (.html, .htm): 直接部署
    - Markdown文件 (.md, .markdown): 自动转换为HTML并部署
    - 文本文件 (.txt): 转换为格式化HTML并部署

    Args:
        file_path: 本地文件的绝对路径或相对路径

    Returns:
        部署结果，包含访问URL和部署信息
    """
    # 转换为Path对象并检查文件是否存在
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise ValueError(f"文件不存在: {path}")

    if not path.is_file():
        raise ValueError(f"路径不是文件: {path}")

    # 检测文件类型
    file_type = detect_file_type(path)

    if file_type == "unknown":
        raise ValueError(
            f"不支持的文件类型: {path.suffix}。支持的格式: .html, .htm, .md, .markdown, .txt"
        )

    # 读取文件内容
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(path, encoding="gb2312") as f:
                content = f.read()
        except UnicodeDecodeError as exc:
            raise ValueError(f"无法读取文件 {path}：编码格式不支持") from exc

    # 使用文件名（不含扩展名）作为标题
    title = path.stem

    # 转换内容为HTML
    html_content = convert_text_to_html(content, file_type, title)

    # 调用内部的部署函数
    return await _deploy_html_content(html_content)


@mcp.tool()
async def get_site_url(site_name: str) -> str:
    """
    获取站点的访问URL。

    Args:
        site_name: 站点名称

    Returns:
        站点的完整访问URL
    """
    config = get_config()
    return urljoin(str(config.base_url), f"/{site_name}")
