#!/bin/bash
set -e

# X-Pages MCP Docker Build Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="x-pages-mcp"
TAG="latest"
PUSH=false
REGISTRY=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--tag)
      TAG="$2"
      shift 2
      ;;
    -n|--name)
      IMAGE_NAME="$2"
      shift 2
      ;;
    -p|--push)
      PUSH=true
      shift
      ;;
    -r|--registry)
      REGISTRY="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  -t, --tag TAG        Set image tag (default: latest)"
      echo "  -n, --name NAME      Set image name (default: x-pages-mcp)"
      echo "  -p, --push           Push image to registry after build"
      echo "  -r, --registry REG   Registry URL (for push)"
      echo "  -h, --help           Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Construct full image name
FULL_IMAGE_NAME="$IMAGE_NAME:$TAG"
if [[ -n "$REGISTRY" ]]; then
  FULL_IMAGE_NAME="$REGISTRY/$FULL_IMAGE_NAME"
fi

echo -e "${BLUE}🐳 Building X-Pages MCP Docker Image${NC}"
echo -e "${BLUE}=====================================\n${NC}"
echo -e "${YELLOW}Image:${NC} $FULL_IMAGE_NAME"
echo -e "${YELLOW}Project Dir:${NC} $PROJECT_DIR"
echo ""

# Check if .env file exists
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
  echo -e "${YELLOW}⚠️  Warning: .env file not found. Make sure to set environment variables when running the container.${NC}"
  echo ""
fi

# Build the image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
cd "$PROJECT_DIR"

docker build \
  -t "$FULL_IMAGE_NAME" \
  -f Dockerfile \
  .

if [[ $? -eq 0 ]]; then
  echo -e "\n${GREEN}✅ Docker image built successfully!${NC}"
else
  echo -e "\n${RED}❌ Docker build failed!${NC}"
  exit 1
fi

# Show image info
echo -e "\n${BLUE}📊 Image Information:${NC}"
docker images "$FULL_IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Push if requested
if [[ "$PUSH" == true ]]; then
  if [[ -z "$REGISTRY" ]]; then
    echo -e "\n${RED}❌ Registry not specified for push. Use -r/--registry option.${NC}"
    exit 1
  fi
  
  echo -e "\n${BLUE}📤 Pushing image to registry...${NC}"
  docker push "$FULL_IMAGE_NAME"
  
  if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Image pushed successfully!${NC}"
  else
    echo -e "${RED}❌ Push failed!${NC}"
    exit 1
  fi
fi

echo -e "\n${GREEN}🎉 Build completed!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Start with docker-compose: ${YELLOW}docker-compose up -d${NC}"
echo -e "2. Or run directly: ${YELLOW}docker run -p 8083:8083 --env-file .env $FULL_IMAGE_NAME${NC}"
echo -e "3. Check health: ${YELLOW}curl http://localhost:8083/health${NC}"