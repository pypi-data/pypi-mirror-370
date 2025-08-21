# X-Pages MCP Docker 部署指南

本指南介绍如何使用 Docker 快速构建和部署 X-Pages MCP HTTP 服务器。

## 🚀 快速开始

### 1. 环境配置

首先创建 `.env` 文件：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
X_PAGES_BASE_URL=https://your-domain.com
X_PAGES_API_TOKEN=your-secret-token
```

### 2. 构建和启动

```bash
# 方式1：使用 docker-compose（推荐）
docker-compose up -d

# 方式2：使用构建脚本
./scripts/docker-build.sh
./scripts/docker-deploy.sh up

# 方式3：手动构建和运行
docker build -t x-pages-mcp .
docker run -d -p 8083:8083 --env-file .env --name x-pages-mcp-http x-pages-mcp
```

### 3. 验证部署

```bash
# 检查服务状态
curl http://localhost:8083/health

# 查看服务信息
curl http://localhost:8083/

# 查看容器日志
docker logs x-pages-mcp-http
```

## 📁 文件说明

- `Dockerfile` - Docker 镜像构建文件
- `docker-compose.yml` - 开发环境配置
- `docker-compose.prod.yml` - 生产环境配置
- `.dockerignore` - Docker 构建忽略文件
- `scripts/docker-build.sh` - 构建脚本
- `scripts/docker-deploy.sh` - 部署脚本

## 🔧 构建脚本使用

### docker-build.sh

```bash
# 基础构建
./scripts/docker-build.sh

# 指定标签和名称
./scripts/docker-build.sh -t v1.0.0 -n my-x-pages-mcp

# 构建并推送到仓库
./scripts/docker-build.sh -t latest -r registry.example.com -p

# 查看帮助
./scripts/docker-build.sh --help
```

### docker-deploy.sh

```bash
# 启动开发环境
./scripts/docker-deploy.sh up

# 启动生产环境
./scripts/docker-deploy.sh --prod up

# 停止服务
./scripts/docker-deploy.sh down

# 查看日志
./scripts/docker-deploy.sh logs

# 查看状态
./scripts/docker-deploy.sh status

# 重新构建并启动
./scripts/docker-deploy.sh build
```

## 🏭 生产环境部署

### 使用生产配置

```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 或使用部署脚本
./scripts/docker-deploy.sh --prod up
```

### 生产环境特性

- 资源限制（CPU: 0.5核，内存: 512MB）
- 自动重启策略
- 日志轮转（最大10MB，保留3个文件）
- 健康检查

## 🔍 监控和维护

### 健康检查

```bash
# HTTP 健康检查
curl -f http://localhost:8083/health

# Docker 健康状态
docker ps --filter "name=x-pages-mcp"
```

### 日志管理

```bash
# 查看实时日志
docker logs -f x-pages-mcp-http

# 查看最近100行日志
docker logs --tail 100 x-pages-mcp-http

# 使用 docker-compose 查看日志
docker-compose logs -f
```

### 性能监控

```bash
# 查看容器资源使用
docker stats x-pages-mcp-http

# 查看镜像信息
docker images x-pages-mcp
```

## 🛠 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :8083
   
   # 修改端口映射
   docker run -p 8084:8083 ...
   ```

2. **环境变量未设置**
   ```bash
   # 检查环境变量
   docker exec x-pages-mcp-http env | grep X_PAGES
   
   # 重新创建容器
   docker-compose down && docker-compose up -d
   ```

3. **健康检查失败**
   ```bash
   # 进入容器调试
   docker exec -it x-pages-mcp-http /bin/bash
   
   # 手动测试健康检查
   curl -v http://localhost:8083/health
   ```

### 调试模式

```bash
# 以交互模式运行
docker run -it --rm -p 8083:8083 --env-file .env x-pages-mcp /bin/bash

# 查看启动日志
docker-compose up
```

## 🌐 网络配置

### 自定义网络

```bash
# 创建自定义网络
docker network create x-pages-network

# 连接到现有网络
docker run --network x-pages-network ...
```

### 反向代理

Nginx 配置示例：

```nginx
upstream x-pages-mcp {
    server localhost:8083;
}

server {
    listen 80;
    server_name mcp.example.com;

    location / {
        proxy_pass http://x-pages-mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📋 环境变量

| 变量名 | 必需 | 描述 | 示例 |
|--------|------|------|------|
| X_PAGES_BASE_URL | 是 | X-Pages 服务基础URL | https://pages.example.com |
| X_PAGES_API_TOKEN | 是 | API 认证令牌 | your-secret-token |

## 🔒 安全建议

1. **生产环境**
   - 使用 HTTPS 端点
   - 定期更新镜像
   - 设置防火墙规则

2. **密钥管理**
   - 不要在镜像中硬编码密钥
   - 使用 Docker Secrets 或外部密钥管理
   - 定期轮换 API 令牌

3. **网络安全**
   - 限制容器网络访问
   - 使用非 root 用户运行
   - 启用容器安全扫描