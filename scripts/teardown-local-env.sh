#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧹 Cleaning up Local E2E Environment${NC}\n"

# Confirm deletion
read -p "This will delete the Kind cluster 'ops-agent-test'. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Delete Kind cluster
if kind get clusters 2>/dev/null | grep -q "ops-agent-test"; then
    echo "🗑️  Deleting Kind cluster..."
    kind delete cluster --name ops-agent-test
    echo -e "${GREEN}✓ Cluster deleted${NC}\n"
else
    echo -e "${YELLOW}⚠️  Cluster 'ops-agent-test' not found${NC}\n"
fi

# Stop LocalStack if running
if command -v docker-compose &> /dev/null; then
    if [ -f "local-dev/localstack/docker-compose.yml" ]; then
        echo "🛑 Stopping LocalStack..."
        docker-compose -f local-dev/localstack/docker-compose.yml down -v 2>/dev/null || true
        echo -e "${GREEN}✓ LocalStack stopped${NC}\n"
    fi
fi

echo -e "${GREEN}✅ Cleanup complete${NC}"
echo -e "${YELLOW}💡 Run 'make setup-local' to recreate the environment${NC}\n"
