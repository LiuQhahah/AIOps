#!/bin/bash
set -e

# OpsAgent K8s 部署脚本
# 用法: ./deploy.sh [install|uninstall|upgrade|status]

NAMESPACE="ops-system"
APP_NAME="opsagent"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function check_prerequisites() {
    log_info "检查先决条件..."

    # 检查 kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl 未安装。请先安装 kubectl。"
        exit 1
    fi

    # 检查集群连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到 Kubernetes 集群。请检查 kubeconfig 配置。"
        exit 1
    fi

    log_info "✓ kubectl 已安装"
    log_info "✓ 集群连接正常"
}

function build_image() {
    log_info "构建 Docker 镜像..."

    cd "${SCRIPT_DIR}/../.."

    # 检查是否有 Docker
    if ! command -v docker &> /dev/null; then
        log_warn "Docker 未安装，跳过镜像构建。"
        log_warn "请手动构建镜像或使用已有镜像。"
        return
    fi

    # 构建镜像
    docker build -t ${APP_NAME}:latest .

    log_info "✓ 镜像构建完成: ${APP_NAME}:latest"
    log_warn "提示: 如果集群无法访问本地镜像，请推送到镜像仓库："
    log_warn "  docker tag ${APP_NAME}:latest your-registry/${APP_NAME}:latest"
    log_warn "  docker push your-registry/${APP_NAME}:latest"
}

function install() {
    log_info "开始安装 OpsAgent..."

    # 1. 创建命名空间
    log_info "创建命名空间..."
    kubectl apply -f "${SCRIPT_DIR}/namespace.yaml"

    # 2. 创建 RBAC
    log_info "创建 RBAC 权限..."
    kubectl apply -f "${SCRIPT_DIR}/rbac.yaml"

    # 3. 创建 ConfigMap
    log_info "创建 ConfigMap..."
    kubectl apply -f "${SCRIPT_DIR}/configmap.yaml"

    # 4. 创建 Secret（如果存在）
    if [ -f "${SCRIPT_DIR}/secret.yaml" ]; then
        log_info "创建 Secret..."
        kubectl apply -f "${SCRIPT_DIR}/secret.yaml"
    else
        log_warn "未找到 secret.yaml，跳过 Secret 创建。"
        log_warn "如需使用云服务凭证，请参考 secret-template.yaml 创建 secret.yaml"
        # 创建空 Secret 避免 Deployment 失败
        kubectl create secret generic ${APP_NAME}-secrets \
            --namespace=${NAMESPACE} \
            --dry-run=client -o yaml | kubectl apply -f -
    fi

    # 5. 创建 Deployment
    log_info "创建 Deployment..."
    kubectl apply -f "${SCRIPT_DIR}/deployment.yaml"

    # 6. 创建 Service
    log_info "创建 Service..."
    kubectl apply -f "${SCRIPT_DIR}/service.yaml"

    log_info "等待 Deployment 就绪..."
    kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE} --timeout=300s

    log_info "✓ OpsAgent 安装完成！"
    echo ""
    show_status
}

function uninstall() {
    log_info "开始卸载 OpsAgent..."

    # 删除所有资源
    kubectl delete -f "${SCRIPT_DIR}/service.yaml" --ignore-not-found=true
    kubectl delete -f "${SCRIPT_DIR}/deployment.yaml" --ignore-not-found=true
    kubectl delete -f "${SCRIPT_DIR}/configmap.yaml" --ignore-not-found=true
    kubectl delete -f "${SCRIPT_DIR}/rbac.yaml" --ignore-not-found=true

    # 询问是否删除 Secret
    read -p "是否删除 Secret？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete secret ${APP_NAME}-secrets -n ${NAMESPACE} --ignore-not-found=true
    fi

    # 询问是否删除命名空间
    read -p "是否删除命名空间 ${NAMESPACE}？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete -f "${SCRIPT_DIR}/namespace.yaml" --ignore-not-found=true
    fi

    log_info "✓ OpsAgent 卸载完成！"
}

function upgrade() {
    log_info "开始升级 OpsAgent..."

    # 更新 ConfigMap
    kubectl apply -f "${SCRIPT_DIR}/configmap.yaml"

    # 重启 Deployment
    kubectl rollout restart deployment/${APP_NAME} -n ${NAMESPACE}

    log_info "等待 Deployment 就绪..."
    kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE} --timeout=300s

    log_info "✓ OpsAgent 升级完成！"
    show_status
}

function show_status() {
    log_info "OpsAgent 状态:"
    echo ""

    # Deployment 状态
    echo "Deployment:"
    kubectl get deployment ${APP_NAME} -n ${NAMESPACE}
    echo ""

    # Pod 状态
    echo "Pods:"
    kubectl get pods -l app=${APP_NAME} -n ${NAMESPACE}
    echo ""

    # Service 状态
    echo "Services:"
    kubectl get service ${APP_NAME} -n ${NAMESPACE}
    echo ""

    # 日志预览
    log_info "最近日志 (最后 10 行):"
    kubectl logs -l app=${APP_NAME} -n ${NAMESPACE} --tail=10 || true
    echo ""

    # 访问信息
    log_info "访问信息:"
    echo "  API 端点: http://${APP_NAME}.${NAMESPACE}.svc.cluster.local"
    echo "  Metrics: http://${APP_NAME}.${NAMESPACE}.svc.cluster.local:9090/metrics"
    echo ""
    log_info "查看完整日志:"
    echo "  kubectl logs -f deployment/${APP_NAME} -n ${NAMESPACE}"
    echo ""
    log_info "进入 Pod:"
    echo "  kubectl exec -it deployment/${APP_NAME} -n ${NAMESPACE} -- /bin/bash"
}

function show_logs() {
    log_info "查看 OpsAgent 日志..."
    kubectl logs -f deployment/${APP_NAME} -n ${NAMESPACE}
}

function exec_shell() {
    log_info "进入 OpsAgent Pod..."
    kubectl exec -it deployment/${APP_NAME} -n ${NAMESPACE} -- /bin/bash
}

function port_forward() {
    local LOCAL_PORT=${1:-18080}
    log_info "端口转发: localhost:${LOCAL_PORT} -> ${APP_NAME}:18080"
    log_info "访问 API: http://localhost:${LOCAL_PORT}"
    log_info "按 Ctrl+C 停止"
    kubectl port-forward -n ${NAMESPACE} deployment/${APP_NAME} ${LOCAL_PORT}:18080
}

function usage() {
    cat <<EOF
OpsAgent Kubernetes 部署工具

用法: $0 [命令]

命令:
  install       安装 OpsAgent
  uninstall     卸载 OpsAgent
  upgrade       升级 OpsAgent
  status        查看 OpsAgent 状态
  logs          查看实时日志
  shell         进入 Pod Shell
  port-forward  端口转发 (默认 18080)
  build         构建 Docker 镜像
  help          显示此帮助信息

示例:
  $0 install              # 安装 OpsAgent
  $0 status               # 查看状态
  $0 logs                 # 查看日志
  $0 port-forward 8080    # 端口转发到本地 8080
  $0 uninstall            # 卸载

EOF
}

# 主逻辑
case "${1:-help}" in
    install)
        check_prerequisites
        build_image
        install
        ;;
    uninstall)
        check_prerequisites
        uninstall
        ;;
    upgrade)
        check_prerequisites
        upgrade
        ;;
    status)
        check_prerequisites
        show_status
        ;;
    logs)
        check_prerequisites
        show_logs
        ;;
    shell)
        check_prerequisites
        exec_shell
        ;;
    port-forward)
        check_prerequisites
        port_forward "${2:-18080}"
        ;;
    build)
        build_image
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        log_error "未知命令: $1"
        usage
        exit 1
        ;;
esac
