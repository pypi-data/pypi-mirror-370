# X-Pages MCP Server

X-Pages MCP Server是一个基于Model Context Protocol (MCP)的HTML部署服务，让AI能够直接部署HTML内容并获取访问URL。项目使用Python实现，基于FastMCP框架构建。

## 🚀 功能特性

- 🤖 **AI友好** - 通过MCP协议让AI直接部署HTML内容
- 🔧 **简单易用** - 几个命令即可完成部署和管理
- 🛡️ **安全认证** - 支持token认证，保护API访问
- 🌐 **即时访问** - 部署后立即获得可访问的网站URL
- 📄 **多格式支持** - 支持HTML、Markdown、TXT等格式文件部署
- 🔄 **完整管理** - 支持部署、删除、URL获取等完整操作

## 📦 安装

### 前置要求

- Python 3.10+
- uv (推荐) 或 pip
- 已部署的X-Pages服务

### 从PyPI安装

```bash
# 使用uvx直接运行（推荐）
uvx x-pages-mcp-stdio
uvx x-pages-mcp-http --port 8083

# 或使用uv安装到虚拟环境
uv add x-pages-mcp
uv run x-pages-mcp-stdio

# 或传统pip方式
pip install x-pages-mcp
x-pages-mcp-stdio
```

### 开发安装

```bash
# 克隆项目
git clone <repository-url>
cd x-pages-mcp

# 安装依赖
uv sync

# 或使用pip安装
pip install -e .
```

## ⚙️ 配置

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

### Claude Desktop 配置

在Claude Desktop的配置文件中添加MCP服务器：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
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
```

## 🚀 使用方法

### 传输模式

X-Pages MCP服务器支持两种传输模式：

#### STDIO模式（用于Claude Desktop）

标准输入输出模式，适合Claude Desktop等本地客户端：

```bash
# STDIO模式
uv run x-pages-mcp-stdio

# 或使用安装后的命令
x-pages-mcp-stdio
```

#### HTTP模式（用于API集成）

基于FastAPI的HTTP API服务，支持Web客户端和API集成：

```bash
# HTTP模式
uv run x-pages-mcp-http --host localhost --port 8083

# HTTP开发模式（支持自动重载）
uv run x-pages-mcp-http --host localhost --port 8083 --reload

# 使用安装后的命令
x-pages-mcp-http --host localhost --port 8083
```

### 开发测试

```bash
# 使用mcp-inspector测试
npx @modelcontextprotocol/inspector uv run x-pages-mcp-stdio

# 运行测试
uv run pytest

# 代码检查和格式化
uv run ruff check src/
uv run ruff format src/

# 类型检查
uv run mypy src/
```

## 🛠 可用工具

### 1. deploy_html
部署HTML内容到X-Pages服务

**参数：**
- `html_content` (string): 完整的HTML内容

**返回：**
```json
{
  "success": true,
  "site_name": "随机生成的24位标识符",
  "deploy_url": "https://your-domain.com/site_name",
  "deployed_at": "2024-01-01T00:00:00Z",
  "content_length": 1024,
  "message": "HTML site deployed successfully"
}
```

### 2. delete_html
从X-Pages服务删除HTML站点

**参数：**
- `site_name` (string): 要删除的站点名称

**返回：**
```json
{
  "success": true,
  "site_name": "my-site",
  "message": "HTML site deleted successfully"
}
```

### 3. get_site_url
获取站点的访问URL

**参数：**
- `site_name` (string): 站点名称

**返回：** `"https://your-domain.com/my-site"`

### 4. create_sample_html
创建示例HTML页面内容

**参数：**
- `title` (string, 可选): HTML页面标题，默认"示例页面"
- `heading` (string, 可选): 页面主标题，默认"Hello World!"
- `content` (string, 可选): 页面内容，默认示例文本

**返回：** 完整的HTML内容，可用于部署

### 5. deploy_file
部署文件到X-Pages服务（支持多种格式）

**参数：**
- `file_path` (string): 要部署的文件路径

**支持的文件格式：**
- HTML文件 (.html, .htm)
- Markdown文件 (.md, .markdown)
- 文本文件 (.txt)

**返回：**
```json
{
  "success": true,
  "site_name": "随机生成的24位标识符",
  "deploy_url": "https://your-domain.com/site_name",
  "deployed_at": "2024-01-01T00:00:00Z",
  "file_type": "markdown",
  "message": "File deployed successfully"
}
```

## 💡 使用示例

### 与Claude Desktop一起使用

配置完成后，你可以在Claude Desktop中直接使用自然语言进行HTML部署：

```
用户：帮我创建一个简单的个人介绍网站并部署

Claude：我来为你创建并部署一个个人介绍网站。

首先，我会创建一个包含个人介绍的HTML页面，然后部署到X-Pages服务。
```

Claude会自动调用MCP工具来：
1. 创建HTML内容
2. 部署到X-Pages服务
3. 返回可访问的网站URL

### 命令行使用

```bash
# 启动STDIO模式的MCP服务器
uv run x-pages-mcp-stdio

# 启动HTTP模式的MCP服务器
uv run x-pages-mcp-http --host localhost --port 8083
```

## 🐳 Docker 部署

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

## 🧪 测试

```bash
# 运行测试
uv run pytest

# 运行测试并显示覆盖率
uv run pytest --cov=x_pages_mcp
```

## 🛡️ 安全注意事项

1. **保护API Token** - 不要在代码中硬编码token，使用环境变量
2. **网络安全** - 确保X-Pages服务使用HTTPS
3. **输入验证** - 对HTML内容进行适当的安全检查
4. **访问控制** - 限制MCP服务器的访问权限

## 🏗️ 项目架构

### 核心组件

1. **MCP工具库** (`src/mcp_servers/xpages_mcp.py`)
   - 基于FastMCP框架实现，使用模块级变量 `mcp = FastMCP("X-Pages HTML Deployment")`
   - 提供5个核心工具：deploy_html, delete_html, get_site_url, create_sample_html, deploy_file
   - 配置通过环境变量管理

2. **STDIO服务器** (`src/x_pages_mcp/stdio_server.py`)
   - STDIO模式的独立启动器，用于Claude Desktop等客户端
   - 直接导入并使用 `mcp` 变量

3. **HTTP服务器** (`src/x_pages_mcp/http_server.py`)
   - HTTP模式的独立启动器，基于FastAPI
   - 支持 `--reload` 开发模式
   - 提供健康检查和根路径信息端点

### 项目架构原则

项目采用**直接变量引用**风格，避免不必要的函数封装：

- **MCP服务器实例**: 使用模块级变量 `mcp = FastMCP(...)` 而非工厂函数
- **FastAPI应用实例**: 使用模块级变量 `app = FastAPI(...)` 而非 `create_app()` 函数
- **直接导入使用**: `from mcp_servers.xpages_mcp import mcp` 直接使用，简洁明了
- **模块级配置**: 配置和初始化在模块导入时完成，运行时直接引用

## 📄 许可证

MIT License

## 🆘 故障排除

### 常见问题

**Q: 配置错误 "X_PAGES_BASE_URL environment variable is required"**
A: 确保设置了正确的环境变量，参考配置部分

**Q: 部署失败 "Invalid token"**
A: 检查X_PAGES_API_TOKEN是否与X-Pages服务中配置的token一致

**Q: 网络请求失败**
A: 检查X_PAGES_BASE_URL是否正确，网络连接是否正常

**Q: Claude Desktop中看不到MCP工具**
A: 检查配置文件路径和格式，重启Claude Desktop

### 调试模式

```bash
# 启用调试日志
export MCP_LOG_LEVEL=DEBUG
uv run x-pages-mcp-stdio
```

## 🔗 相关链接

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Claude Desktop MCP 配置文档](https://docs.anthropic.com/en/docs/build-with-claude/computer-use)