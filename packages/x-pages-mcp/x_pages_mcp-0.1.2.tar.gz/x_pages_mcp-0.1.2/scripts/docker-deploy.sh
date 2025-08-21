#!/bin/bash
set -e

# X-Pages MCP Docker Deploy Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MODE="dev"
COMPOSE_FILE="docker-compose.yml"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --prod)
      MODE="prod"
      COMPOSE_FILE="docker-compose.prod.yml"
      shift
      ;;
    --dev)
      MODE="dev"
      COMPOSE_FILE="docker-compose.yml"
      shift
      ;;
    -f|--file)
      COMPOSE_FILE="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [options] [command]"
      echo ""
      echo "Options:"
      echo "  --dev               Use development configuration (default)"
      echo "  --prod              Use production configuration"
      echo "  -f, --file FILE     Use specific compose file"
      echo "  -h, --help          Show this help message"
      echo ""
      echo "Commands:"
      echo "  up                  Start services (default)"
      echo "  down                Stop services"
      echo "  restart             Restart services"
      echo "  logs                Show logs"
      echo "  status              Show service status"
      echo "  build               Build and start services"
      exit 0
      ;;
    *)
      COMMAND="$1"
      shift
      ;;
  esac
done

# Default command
if [[ -z "$COMMAND" ]]; then
  COMMAND="up"
fi

echo -e "${BLUE}🚀 X-Pages MCP Docker Deploy${NC}"
echo -e "${BLUE}============================\n${NC}"
echo -e "${YELLOW}Mode:${NC} $MODE"
echo -e "${YELLOW}Compose File:${NC} $COMPOSE_FILE"
echo -e "${YELLOW}Command:${NC} $COMMAND"
echo ""

cd "$PROJECT_DIR"

# Check if .env file exists
if [[ ! -f ".env" ]]; then
  echo -e "${RED}❌ Error: .env file not found!${NC}"
  echo -e "${YELLOW}Please create a .env file with the following variables:${NC}"
  echo "X_PAGES_BASE_URL=https://your-domain.com"
  echo "X_PAGES_API_TOKEN=your-secret-token"
  exit 1
fi

# Check if compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo -e "${RED}❌ Error: Compose file '$COMPOSE_FILE' not found!${NC}"
  exit 1
fi

# Execute command
case $COMMAND in
  up)
    echo -e "${BLUE}🔄 Starting services...${NC}"
    if [[ "$MODE" == "prod" ]]; then
      docker-compose -f "$COMPOSE_FILE" up -d
    else
      docker-compose -f "$COMPOSE_FILE" up -d
    fi
    
    echo -e "\n${BLUE}⏳ Waiting for service to be ready...${NC}"
    sleep 5
    
    # Health check
    if curl -f http://localhost:8083/health >/dev/null 2>&1; then
      echo -e "${GREEN}✅ Service is healthy!${NC}"
    else
      echo -e "${YELLOW}⚠️  Service may still be starting up...${NC}"
    fi
    
    echo -e "\n${GREEN}🎉 Services started successfully!${NC}"
    echo -e "${BLUE}Access the service at: ${YELLOW}http://localhost:8083${NC}"
    echo -e "${BLUE}Health check: ${YELLOW}http://localhost:8083/health${NC}"
    echo -e "${BLUE}MCP endpoint: ${YELLOW}http://localhost:8083/llm/mcp${NC}"
    ;;
    
  down)
    echo -e "${BLUE}🛑 Stopping services...${NC}"
    docker-compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✅ Services stopped!${NC}"
    ;;
    
  restart)
    echo -e "${BLUE}🔄 Restarting services...${NC}"
    docker-compose -f "$COMPOSE_FILE" restart
    echo -e "${GREEN}✅ Services restarted!${NC}"
    ;;
    
  logs)
    echo -e "${BLUE}📋 Showing logs...${NC}"
    docker-compose -f "$COMPOSE_FILE" logs -f
    ;;
    
  status)
    echo -e "${BLUE}📊 Service Status:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    echo -e "${BLUE}📊 Docker Images:${NC}"
    docker images x-pages-mcp
    ;;
    
  build)
    echo -e "${BLUE}🔨 Building and starting services...${NC}"
    docker-compose -f "$COMPOSE_FILE" up --build -d
    
    echo -e "\n${BLUE}⏳ Waiting for service to be ready...${NC}"
    sleep 5
    
    # Health check
    if curl -f http://localhost:8083/health >/dev/null 2>&1; then
      echo -e "${GREEN}✅ Service is healthy!${NC}"
    else
      echo -e "${YELLOW}⚠️  Service may still be starting up...${NC}"
    fi
    
    echo -e "${GREEN}✅ Build and deploy completed!${NC}"
    ;;
    
  *)
    echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
    echo "Use --help for available commands."
    exit 1
    ;;
esac