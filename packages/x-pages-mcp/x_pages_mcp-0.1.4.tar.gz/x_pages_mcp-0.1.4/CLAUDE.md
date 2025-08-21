# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

X-Pages MCP Server是一个基于Model Context Protocol (MCP)的HTML部署服务，让AI能够直接部署HTML内容并获取访问URL。项目使用Python实现，基于FastMCP框架构建。

## 相关技术框架
- python 3.10+
- fastmcp 是用 FastMCP2.0 (jlowin/fastmcp) 来实现
- fastapi 网络服务库

## 代码架构原则

项目采用**直接变量引用**风格，避免不必要的函数封装：

- **MCP服务器实例**: 使用模块级变量 `mcp = FastMCP(...)` 而非工厂函数
- **FastAPI应用实例**: 使用模块级变量 `app = FastAPI(...)` 而非 `create_app()` 函数
- **直接导入使用**: `from mcp_servers.xpages_mcp import mcp` 直接使用，简洁明了
- **模块级配置**: 配置和初始化在模块导入时完成，运行时直接引用

这种风格的优势：
- 更简洁的代码结构
- 更直观的导入和使用方式
- 减少不必要的函数调用开销
- 符合Python模块化设计原则


## 开发命令

### 环境设置和依赖管理
```bash
# 安装依赖
uv sync

# 或使用pip安装
pip install -e .
```

### 运行和测试
```bash
# 统一入口点（推荐）
uv run x-pages-mcp stdio              # STDIO模式
uv run x-pages-mcp http               # HTTP模式
uv run x-pages-mcp http --port 8080   # HTTP模式，指定端口
uv run x-pages-mcp http --reload      # HTTP开发模式

# 传统入口点（向后兼容）
uv run x-pages-mcp-stdio              # STDIO模式
uv run x-pages-mcp-http               # HTTP模式

# 运行测试
uv run pytest

# 测试MCP服务器
npx @modelcontextprotocol/inspector uv run x-pages-mcp stdio
```

### 代码质量检查
```bash
# 代码检查和格式化
uv run ruff check src/
uv run ruff format src/

# 类型检查
uv run mypy src/
```

## 项目架构

### 核心组件

1. **MCP工具库** (`src/mcp_servers/xpages_mcp.py`)
   - 基于FastMCP框架实现，使用模块级变量 `mcp = FastMCP("X-Pages HTML Deployment")`
   - 提供3个核心工具：deploy_html, delete_html, get_site_url
   - 配置通过环境变量管理 (`get_config_from_env()`)
   - 所有工具函数直接使用 `@mcp.tool()` 装饰器

2. **STDIO服务器** (`src/x_pages_mcp/stdio_server.py`)
   - STDIO模式的独立启动器，用于Claude Desktop等客户端
   - 直接导入并使用 `mcp` 变量，调用 `mcp.run(transport="stdio")`
   - 环境变量验证和错误处理

3. **HTTP服务器** (`src/x_pages_mcp/http_server.py`)
   - HTTP模式的独立启动器，基于FastAPI
   - 使用模块级变量 `app = FastAPI(...)` 和 `mcp_app = mcp.http_app(path="/mcp")`
   - 支持 `--reload` 开发模式，通过导入字符串加载应用
   - 提供健康检查和根路径信息端点

4. **统一启动器** (`start_server.py`)
   - 兼容性启动入口，委托给具体的服务器模块
   - 命令行参数解析和传递
   - 环境变量检查

### 关键数据流

1. **HTML部署流程**：
   - 生成24位随机站点名称 (`generate_site_name()`)
   - 构建API请求到X-Pages服务 (`/html/deploy`)
   - 返回访问URL和部署信息

2. **配置管理**：
   - `XPagesConfig` Pydantic模型管理配置
   - 必需环境变量：`X_PAGES_BASE_URL`, `X_PAGES_API_TOKEN`
   - 固定超时时间：30秒

### 传输模式说明

- **STDIO模式**：用于Claude Desktop等本地客户端，通过标准输入输出通信，配置通过环境变量提供
- **HTTP模式**：基于FastAPI的HTTP API服务，支持Web客户端和API集成，默认端口为8083，也使用环境变量配置

## 配置说明

### 环境变量配置

所有模式都使用相同的环境变量配置：

#### 方法1：使用 .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```bash
X_PAGES_BASE_URL=https://your-domain.com
X_PAGES_API_TOKEN=your-secret-token
```

#### 方法2：直接设置环境变量

```bash
export X_PAGES_BASE_URL=https://your-domain.com
export X_PAGES_API_TOKEN=your-secret-token
```


## Claude Desktop配置示例

配置文件位置：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
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
```

## 安装和使用

### 从 PyPI 安装

```bash
# 使用 uvx 运行（推荐）
uvx x-pages-mcp stdio

# 或安装后使用
pip install x-pages-mcp
x-pages-mcp stdio
```

### 开发测试

```bash
# 使用 fastmcp cli 测试
uv run fastmcp dev src/stdio_server.py

# 使用 mcp-inspector 测试
npx @modelcontextprotocol/inspector uv run x-pages-mcp stdio
```

### 可用命令

```bash
# 查看帮助
x-pages-mcp --help

# 统一入口点（推荐）
x-pages-mcp stdio              # STDIO模式
x-pages-mcp http               # HTTP模式，默认localhost:8083
x-pages-mcp http --port 8080   # HTTP模式，指定端口
x-pages-mcp http --reload      # HTTP开发模式

# 传统命令（向后兼容）
x-pages-mcp-stdio --help
x-pages-mcp-http --help
```

## Docker 部署

### 快速启动

```bash
# 创建环境变量文件
cp .env.example .env
# 编辑 .env 文件设置 X_PAGES_BASE_URL 和 X_PAGES_API_TOKEN

# 使用 docker-compose 启动
docker-compose up -d

# 检查服务状态
curl http://localhost:8083/health
```

### 构建和部署脚本

```bash
# 构建 Docker 镜像
./scripts/docker-build.sh

# 部署服务
./scripts/docker-deploy.sh up          # 开发环境
./scripts/docker-deploy.sh --prod up   # 生产环境

# 查看日志
./scripts/docker-deploy.sh logs

# 停止服务
./scripts/docker-deploy.sh down
```

详细的 Docker 部署指南请查看 `docker/README.md`。

## 📦 打包发布

### 版本管理

项目版本信息在 `pyproject.toml` 中管理：

```toml
[project]
version = "0.1.1"
```

### 发布前检查

在发布之前，请确保：

```bash
# 1. 同步依赖（如果需要）
uv sync --dev

# 2. 代码质量检查
uv run ruff check src/
uv run ruff format src/

# 3. 类型检查  
uv run mypy src/

# 4. 运行测试
uv run pytest

# 5. 检查打包配置
uv run python -c "import tomllib; f=open('pyproject.toml','rb'); print('✓ pyproject.toml 格式正确')"
```

### 快速验证流程（基于uv）

```bash
# 一键完整验证流程
uv sync --dev                    # 同步依赖
uv run ruff check src/           # 代码检查
uv run ruff format src/          # 代码格式化
uv run mypy src/                 # 类型检查
uv run pytest                   # 运行测试
uv build                        # 构建包
uv run twine check dist/*        # 验证包
```

### 构建和发布流程

#### 1. 更新版本号

```bash
# 在 pyproject.toml 中更新版本号
# version = "0.1.2"  # 示例版本号
```

#### 2. 构建Python包

```bash
# 清理之前的构建产物
rm -rf dist/ build/ *.egg-info/

# 使用uv构建包
uv build

# 验证构建产物
ls -la dist/
# 应该看到：
# x_pages_mcp-0.1.1-py3-none-any.whl
# x_pages_mcp-0.1.1.tar.gz
```

#### 3. 验证包内容

```bash
# 检查包内容
uv run python -m tarfile -l dist/x_pages_mcp-0.1.1.tar.gz

# 检查包的元数据
uv run twine check dist/*
```

#### 4. 测试安装（可选）

```bash
# 使用uv创建临时环境测试安装
uv venv test_env
source test_env/bin/activate  # macOS/Linux
# 或 test_env\Scripts\activate  # Windows

# 使用uv安装本地构建的包
uv pip install dist/x_pages_mcp-0.1.1-py3-none-any.whl

# 测试命令行工具是否正确安装
which x-pages-mcp-stdio
which x-pages-mcp-http

# 测试工具帮助信息
x-pages-mcp-stdio --help
x-pages-mcp-http --help

# 验证包导入
python -c "import mcp_servers.xpages_mcp; print('✓ 包导入成功')"
python -c "import stdio_server; print('✓ STDIO服务器模块正常')"
python -c "import http_server; print('✓ HTTP服务器模块正常')"

# 清理测试环境
deactivate
rm -rf test_env
```

#### 5. 发布到PyPI

```bash
# 发布到测试PyPI（推荐先测试）
uv run twine upload --repository testpypi dist/*

# 从测试PyPI安装验证
uv pip install --index-url https://test.pypi.org/simple/ x-pages-mcp

# 发布到正式PyPI
uv run twine upload dist/*
```

### PyPI认证配置

#### 使用API Token（推荐）

```bash
# 创建 ~/.pypirc 文件
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
EOF

# 设置安全权限
chmod 600 ~/.pypirc
```

#### 使用环境变量

```bash
# 设置环境变量
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here

# 或者只为测试PyPI设置
export TWINE_REPOSITORY=testpypi
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-test-token-here
```

### 发布后验证

```bash
# 等待几分钟后，从PyPI安装验证
uv pip install --upgrade x-pages-mcp

# 或使用uvx直接运行
uvx x-pages-mcp-stdio --help
uvx x-pages-mcp-http --help

# 验证版本信息
python -c "import x_pages_mcp; print(x_pages_mcp.__version__)"
```

### 发布检查清单

发布前请确保：

- [ ] 版本号已更新（遵循语义化版本）
- [ ] README.md 已更新相关版本信息
- [ ] 所有测试通过
- [ ] 代码格式化和类型检查通过
- [ ] 打包配置正确（pyproject.toml）
- [ ] 构建产物验证无误
- [ ] 在测试PyPI验证安装成功
- [ ] 准备好发布说明和更新日志

### 自动化发布（可选）

可以创建GitHub Actions工作流自动化发布过程：

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Install uv
      uses: astral-sh/setup-uv@v1
      with:
        enable-cache: true
    - name: Set up Python
      run: uv python install 3.10
    - name: Install dependencies
      run: uv sync --dev
    - name: Run quality checks
      run: |
        uv run ruff check src/
        uv run ruff format --check src/
        uv run mypy src/
    - name: Run tests
      run: uv run pytest
    - name: Build package
      run: uv build
    - name: Check package
      run: uv run twine check dist/*
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```


## 安全注意事项

- **生产环境**：X-Pages服务端点必须使用HTTPS
- **API密钥保护**：X-Pages API token应该妥善保管，通过环境变量传递

