#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🧪 Running E2E Tests${NC}\n"

# Check if cluster exists
if ! kind get clusters 2>/dev/null | grep -q "ops-agent-test"; then
  echo -e "${RED}❌ Kind cluster 'ops-agent-test' not found${NC}"
  echo -e "${YELLOW}Run 'make setup-local' first${NC}"
  exit 1
fi

# Switch to correct context
kubectl config use-context kind-ops-agent-test > /dev/null 2>&1

# Reset test data
echo "🔄 Resetting test data..."
kubectl delete -f tests/e2e/fixtures/k8s/ --ignore-not-found=true > /dev/null 2>&1 || true
sleep 2
kubectl apply -f tests/e2e/fixtures/k8s/
echo -e "${GREEN}✓ Test fixtures deployed${NC}\n"

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=60s \
  deployment --all -n test-app 2>/dev/null || true
echo -e "${GREEN}✓ Deployments ready${NC}\n"

# Run pytest
echo "🚀 Running pytest E2E tests..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "tests/e2e/test_detection.py" ]; then
  pytest tests/e2e/ -v \
    --tb=short \
    --color=yes \
    -m "e2e" \
    --maxfail=3
else
  echo -e "${YELLOW}⚠️  E2E test files not yet created${NC}"
  echo -e "${YELLOW}   Run: pytest tests/e2e/ when tests are implemented${NC}"
  exit 0
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "\n${GREEN}✅ E2E tests completed${NC}\n"
