#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up Multi-Cloud OpsAgent Local E2E Environment${NC}\n"

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."

    local missing=0

    if ! command -v kind &> /dev/null; then
        echo -e "${RED}❌ kind not found. Install: https://kind.sigs.k8s.io/docs/user/quick-start/#installation${NC}"
        missing=1
    else
        echo -e "${GREEN}✓${NC} kind $(kind version | cut -d' ' -f2)"
    fi

    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/${NC}"
        missing=1
    else
        echo -e "${GREEN}✓${NC} kubectl $(kubectl version --client --short 2>/dev/null || echo 'installed')"
    fi

    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ docker not found. Install: https://docs.docker.com/get-docker/${NC}"
        missing=1
    else
        echo -e "${GREEN}✓${NC} docker $(docker --version | cut -d' ' -f3 | tr -d ',')"
    fi

    if [ $missing -eq 1 ]; then
        echo -e "\n${RED}Please install missing prerequisites and try again.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ All prerequisites satisfied${NC}\n"
}

# Create Kind cluster
create_cluster() {
    echo "📦 Creating Kind cluster..."

    # Check if cluster already exists
    if kind get clusters 2>/dev/null | grep -q "ops-agent-test"; then
        echo -e "${YELLOW}⚠️  Cluster 'ops-agent-test' already exists${NC}"
        read -p "Delete and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kind delete cluster --name ops-agent-test
        else
            echo "Using existing cluster..."
            return
        fi
    fi

    kind create cluster --config local-dev/kind/kind-config.yaml --wait 3m

    echo -e "${GREEN}✓ Cluster created${NC}\n"
}

# Wait for cluster to be ready
wait_for_cluster() {
    echo "⏳ Waiting for cluster to be ready..."

    kubectl wait --for=condition=Ready nodes --all --timeout=300s

    echo -e "${GREEN}✓ Cluster is ready${NC}\n"
}

# Create namespaces
create_namespaces() {
    echo "📝 Creating namespaces..."

    kubectl create namespace test-app --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace ops-agent --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

    echo -e "${GREEN}✓ Namespaces created${NC}\n"
}

# Deploy test applications with issues
deploy_test_apps() {
    echo "🐛 Deploying test applications (with intentional issues)..."

    if [ -d "tests/e2e/fixtures/k8s" ] && [ "$(ls -A tests/e2e/fixtures/k8s/*.yaml 2>/dev/null)" ]; then
        kubectl apply -f tests/e2e/fixtures/k8s/ --recursive
        echo -e "${GREEN}✓ Test applications deployed${NC}\n"
    else
        echo -e "${YELLOW}⚠️  No test fixtures found yet (will be created in next step)${NC}\n"
    fi
}

# Setup local Git repository
setup_git_repo() {
    echo "📚 Setting up local IaC Git repository..."

    cd local-dev/test-manifests

    if [ -d ".git" ]; then
        echo -e "${YELLOW}⚠️  Git repository already initialized${NC}"
    else
        git init
        git config user.name "OpsAgent Test"
        git config user.email "ops-agent-test@example.com"

        # Create initial structure
        mkdir -p k8s/deployments terraform/{aws,azure}

        # Create initial commit
        cat > README.md << 'EOF'
# Test IaC Repository

This is a local Git repository for testing OpsAgent's GitOps workflow.

## Structure
- `k8s/` - Kubernetes manifests
- `terraform/aws/` - AWS Terraform configs
- `terraform/azure/` - Azure Terraform configs
EOF

        git add .
        git commit -m "Initial commit"

        echo -e "${GREEN}✓ Git repository initialized${NC}"
    fi

    cd ../..
    echo
}

# Create kubeconfig context
setup_kubeconfig() {
    echo "🔧 Setting up kubeconfig context..."

    kubectl config use-context kind-ops-agent-test

    echo -e "${GREEN}✓ Kubeconfig context set${NC}\n"
}

# Print summary
print_summary() {
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Local E2E Environment Ready!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

    echo "📌 Cluster Information:"
    echo "  • Name: ops-agent-test"
    echo "  • Nodes: $(kubectl get nodes --no-headers | wc -l | tr -d ' ')"
    echo "  • Context: kind-ops-agent-test"
    echo

    echo "📦 Namespaces:"
    kubectl get namespaces | grep -E "test-app|ops-agent|monitoring" | awk '{printf "  • %s\n", $1}'
    echo

    echo "🔍 Next Steps:"
    echo "  1. Create test fixtures:      Edit tests/e2e/fixtures/k8s/"
    echo "  2. Deploy test apps:          kubectl apply -f tests/e2e/fixtures/k8s/"
    echo "  3. Run OpsAgent locally:      make run-agent-local"
    echo "  4. Inject issues:             make inject-issue"
    echo "  5. Run E2E tests:             make test-e2e"
    echo "  6. View logs:                 make logs"
    echo

    echo "🛠️  Useful Commands:"
    echo "  • kubectl get pods -A"
    echo "  • kubectl get nodes"
    echo "  • kind get clusters"
    echo "  • kubectl config current-context"
    echo

    echo -e "${YELLOW}💡 Tip: Run 'make clean-local' to teardown the environment${NC}\n"
}

# Main execution
main() {
    check_prerequisites
    create_cluster
    wait_for_cluster
    create_namespaces
    setup_git_repo
    setup_kubeconfig
    deploy_test_apps
    print_summary
}

# Run main function
main
