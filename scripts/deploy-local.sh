#!/bin/bash

# 本地 Kind 集群部署脚本
# 用于快速在本地开发和测试 OpsAgent

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
CLUSTER_NAME="opsagent-dev"
IMAGE_NAME="opsagent"
IMAGE_TAG="latest"
NAMESPACE="ops-system"

# 打印带颜色的消息
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查前置条件
check_prerequisites() {
    info "检查前置条件..."
    check_command docker
    check_command kubectl
    check_command kind
    success "所有前置条件已满足"
}

# 创建 kind 集群
create_cluster() {
    info "创建 kind 集群: $CLUSTER_NAME"

    if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        warn "集群 $CLUSTER_NAME 已存在"
        read -p "是否删除并重新创建? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            delete_cluster
        else
            info "使用现有集群"
            return
        fi
    fi

    if [ -f "kind-config.yaml" ]; then
        kind create cluster --config kind-config.yaml --name $CLUSTER_NAME
    else
        kind create cluster --name $CLUSTER_NAME
    fi

    # 等待集群就绪
    kubectl wait --for=condition=Ready nodes --all --timeout=60s

    success "集群创建成功"
    kubectl cluster-info --context kind-$CLUSTER_NAME
}

# 删除集群
delete_cluster() {
    info "删除 kind 集群: $CLUSTER_NAME"

    if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        warn "集群 $CLUSTER_NAME 不存在"
        return
    fi

    kind delete cluster --name $CLUSTER_NAME
    success "集群已删除"
}

# 构建镜像
build_image() {
    info "构建 Docker 镜像..."
    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
    success "镜像构建完成: ${IMAGE_NAME}:${IMAGE_TAG}"
}

# 加载镜像到 kind
load_image() {
    info "加载镜像到 kind 集群..."

    if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        error "集群 $CLUSTER_NAME 不存在，请先创建集群"
        exit 1
    fi

    kind load docker-image ${IMAGE_NAME}:${IMAGE_TAG} --name $CLUSTER_NAME
    success "镜像已加载到 kind 集群"
}

# 部署应用
deploy_app() {
    info "部署应用到集群..."

    # 确保使用正确的 context
    kubectl config use-context kind-$CLUSTER_NAME

    # 创建 namespace
    info "创建 namespace: $NAMESPACE"
    kubectl get namespace $NAMESPACE || kubectl create namespace $NAMESPACE

    # 部署 RBAC
    info "部署 RBAC..."
    kubectl apply -f deploy/k8s/rbac.yaml

    # 部署 ConfigMap
    info "部署 ConfigMap..."
    kubectl apply -f deploy/k8s/configmap.yaml

    # 部署应用（修改 imagePullPolicy）
    info "部署应用..."
    cat deploy/k8s/deployment.yaml | \
        sed "s|image: opsagent:latest|image: ${IMAGE_NAME}:${IMAGE_TAG}|g" | \
        sed "s|imagePullPolicy: Always|imagePullPolicy: Never|g" | \
        kubectl apply -f -

    # 部署 Service
    info "部署 Service..."
    kubectl apply -f deploy/k8s/service.yaml

    # 等待部署就绪
    info "等待部署就绪..."
    kubectl rollout status deployment/opsagent -n $NAMESPACE --timeout=3m

    success "应用部署完成"
}

# 查看状态
show_status() {
    info "查看部署状态..."

    echo ""
    echo "========================================="
    echo "📊 Deployment Status"
    echo "========================================="
    kubectl get deployment opsagent -n $NAMESPACE || true

    echo ""
    echo "========================================="
    echo "🏃 Pods Status"
    echo "========================================="
    kubectl get pods -n $NAMESPACE -l app=opsagent -o wide || true

    echo ""
    echo "========================================="
    echo "🌐 Service Status"
    echo "========================================="
    kubectl get svc opsagent -n $NAMESPACE || true

    echo ""
    echo "========================================="
    echo "📍 Access Information"
    echo "========================================="
    echo "Run the following command to access the application:"
    echo ""
    echo "  kubectl port-forward -n $NAMESPACE svc/opsagent 18080:80"
    echo ""
    echo "Then access:"
    echo "  - API: http://localhost:18080"
    echo "  - Health: http://localhost:18080/health"
    echo ""
}

# 查看日志
show_logs() {
    info "显示应用日志..."
    kubectl logs -f -n $NAMESPACE -l app=opsagent --tail=100
}

# 端口转发
port_forward() {
    local port=${1:-18080}
    success "端口转发: localhost:$port -> ops-system/opsagent:80"
    echo ""
    echo "访问地址:"
    echo "  - API: http://localhost:$port"
    echo "  - Health: http://localhost:$port/health"
    echo ""
    echo "按 Ctrl+C 停止"
    echo ""
    kubectl port-forward -n $NAMESPACE svc/opsagent $port:80
}

# 完整部署（构建 + 加载 + 部署）
full_deploy() {
    check_prerequisites
    build_image
    load_image
    deploy_app
    show_status
}

# 快速重部署（用于开发迭代）
redeploy() {
    info "快速重部署..."
    build_image
    load_image

    info "重启 deployment..."
    kubectl rollout restart deployment/opsagent -n $NAMESPACE
    kubectl rollout status deployment/opsagent -n $NAMESPACE --timeout=3m

    success "重部署完成"
    show_status
}

# 健康检查
health_check() {
    info "执行健康检查..."

    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=opsagent -o jsonpath='{.items[0].metadata.name}')

    if [ -z "$POD_NAME" ]; then
        error "未找到运行中的 Pod"
        exit 1
    fi

    info "Pod: $POD_NAME"

    # 等待 Pod ready
    kubectl wait --for=condition=ready pod/$POD_NAME -n $NAMESPACE --timeout=60s

    # 测试健康检查端点
    info "测试健康检查端点..."
    kubectl exec -n $NAMESPACE $POD_NAME -- curl -f http://localhost:18080/health

    success "健康检查通过"
}

# 清理资源
cleanup() {
    info "清理资源..."

    kubectl delete -f deploy/k8s/service.yaml --ignore-not-found=true
    kubectl delete -f deploy/k8s/deployment.yaml --ignore-not-found=true
    kubectl delete -f deploy/k8s/configmap.yaml --ignore-not-found=true
    kubectl delete -f deploy/k8s/rbac.yaml --ignore-not-found=true

    read -p "是否删除 namespace $NAMESPACE? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace $NAMESPACE --ignore-not-found=true
    fi

    success "资源清理完成"
}

# 显示帮助
show_help() {
    cat << EOF
OpsAgent Kind 本地部署工具

用法: $0 <命令> [选项]

命令:
  create        创建 kind 集群
  delete        删除 kind 集群
  build         构建 Docker 镜像
  load          加载镜像到 kind 集群
  deploy        部署应用到集群
  full          完整部署（构建 + 加载 + 部署）
  redeploy      快速重部署（开发迭代用）
  status        查看部署状态
  logs          查看应用日志
  port-forward  端口转发 [端口，默认 18080]
  health        健康检查
  cleanup       清理资源
  help          显示此帮助信息

示例:
  $0 create                    # 创建集群
  $0 full                      # 完整部署
  $0 redeploy                  # 快速重部署
  $0 status                    # 查看状态
  $0 logs                      # 查看日志
  $0 port-forward              # 端口转发到 18080
  $0 port-forward 8080         # 端口转发到 8080
  $0 health                    # 健康检查
  $0 cleanup                   # 清理资源
  $0 delete                    # 删除集群

开发工作流:
  1. $0 create                 # 首次创建集群
  2. $0 full                   # 首次完整部署
  3. 修改代码...
  4. $0 redeploy               # 快速重部署
  5. $0 logs                   # 查看日志
  6. 重复步骤 3-5

EOF
}

# 主函数
main() {
    case "${1:-help}" in
        create)
            check_prerequisites
            create_cluster
            ;;
        delete)
            delete_cluster
            ;;
        build)
            build_image
            ;;
        load)
            check_prerequisites
            load_image
            ;;
        deploy)
            check_prerequisites
            deploy_app
            show_status
            ;;
        full)
            full_deploy
            ;;
        redeploy)
            redeploy
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        port-forward)
            port_forward ${2:-18080}
            ;;
        health)
            health_check
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
