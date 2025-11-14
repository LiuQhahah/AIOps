# Kind 本地开发环境快速指南

在本地使用 kind (Kubernetes IN Docker) 运行 OpsAgent，完美的本地开发和测试环境！

## 🎯 什么是 Kind?

**Kind** = **K**ubernetes **IN** **D**ocker

- 在 Docker 容器中运行 Kubernetes 集群
- 完全本地运行，无需云服务
- 快速创建和销毁集群
- 完美适合开发和测试

## ⚡ 5 分钟快速开始

### 步骤 1: 安装 kind (2 分钟)

```bash
# macOS
brew install kind

# Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Windows (使用 PowerShell)
curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.20.0/kind-windows-amd64
Move-Item .\kind-windows-amd64.exe c:\some-dir-in-your-PATH\kind.exe

# 验证安装
kind version
```

### 步骤 2: 创建 kind 集群 (1 分钟)

```bash
# 使用项目提供的配置文件创建集群
kind create cluster --config kind-config.yaml

# 输出示例:
# Creating cluster "opsagent-dev" ...
# ✓ Ensuring node image (kindest/node:v1.27.3) 🖼
# ✓ Preparing nodes 📦
# ✓ Writing configuration 📜
# ✓ Starting control-plane 🕹️
# ✓ Installing CNI 🔌
# ✓ Installing StorageClass 💾
# Set kubectl context to "kind-opsagent-dev"
```

### 步骤 3: 验证集群 (1 分钟)

```bash
# 查看集群
kind get clusters
# 输出: opsagent-dev

# 查看节点
kubectl get nodes
# 输出:
# NAME                         STATUS   ROLES           AGE   VERSION
# opsagent-dev-control-plane   Ready    control-plane   1m    v1.27.3

# 查看 kubectl 上下文
kubectl config current-context
# 输出: kind-opsagent-dev
```

### 步骤 4: 部署应用 (1 分钟)

```bash
# 方式 1: 使用本地部署脚本（推荐）
./scripts/deploy-local.sh

# 方式 2: 手动部署
docker build -t opsagent:latest .
kind load docker-image opsagent:latest --name opsagent-dev
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/rbac.yaml
kubectl apply -f deploy/k8s/configmap.yaml
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml

# 等待部署完成
kubectl rollout status deployment/opsagent -n ops-system
```

### 步骤 5: 访问应用

```bash
# 端口转发到本地
kubectl port-forward -n ops-system svc/opsagent 18080:80

# 在另一个终端访问
curl http://localhost:18080/health

# 或在浏览器打开
open http://localhost:18080
```

## 🚀 完整安装步骤

### 前置要求

| 软件 | 版本 | 安装 |
|------|------|------|
| Docker | 20.10+ | [Install Docker](https://docs.docker.com/get-docker/) |
| kubectl | 1.19+ | [Install kubectl](https://kubernetes.io/docs/tasks/tools/) |
| kind | 0.17+ | 见上方安装命令 |

### 详细步骤

#### 1. 安装和验证 Docker

```bash
# 启动 Docker Desktop (macOS/Windows)
# 或启动 Docker 服务 (Linux)
sudo systemctl start docker

# 验证 Docker
docker version
docker ps

# 确保 Docker 有足够的资源
# Docker Desktop: Preferences → Resources
# 推荐: 4 CPU, 8GB Memory
```

#### 2. 创建 kind 集群

```bash
# 查看配置文件
cat kind-config.yaml

# 创建集群
kind create cluster --config kind-config.yaml --name opsagent-dev

# 如果需要自定义配置
kind create cluster --name opsagent-dev \
  --config kind-config.yaml \
  --image kindest/node:v1.27.3

# 查看集群信息
kubectl cluster-info --context kind-opsagent-dev
```

#### 3. 配置集群（可选）

```bash
# 安装 Metrics Server（用于资源监控）
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 修补 metrics-server 以适配 kind
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

# 等待就绪
kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=60s
```

#### 4. 构建和加载镜像

```bash
# 构建应用镜像
docker build -t opsagent:latest .

# 查看镜像
docker images | grep opsagent

# 加载镜像到 kind 集群
kind load docker-image opsagent:latest --name opsagent-dev

# 验证镜像已加载
docker exec -it opsagent-dev-control-plane crictl images | grep opsagent
```

#### 5. 部署应用

```bash
# 创建命名空间
kubectl apply -f deploy/k8s/namespace.yaml

# 部署 RBAC
kubectl apply -f deploy/k8s/rbac.yaml

# 部署 ConfigMap
kubectl apply -f deploy/k8s/configmap.yaml

# 部署应用（需要修改 imagePullPolicy）
# 临时修改 deployment.yaml 中的:
# imagePullPolicy: Always -> imagePullPolicy: Never

kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml

# 或使用 sed 临时修改
cat deploy/k8s/deployment.yaml | \
  sed 's/imagePullPolicy: Always/imagePullPolicy: Never/g' | \
  kubectl apply -f -
```

#### 6. 验证部署

```bash
# 查看所有资源
kubectl get all -n ops-system

# 查看 Pod 状态
kubectl get pods -n ops-system -w

# 查看日志
kubectl logs -f -n ops-system -l app=opsagent

# 检查健康状态
POD_NAME=$(kubectl get pods -n ops-system -l app=opsagent -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n ops-system $POD_NAME -- curl -f http://localhost:18080/health
```

## 🛠️ 本地开发工作流

### 开发 → 测试 → 部署循环

```bash
# 1. 修改代码
vim src/main.py

# 2. 重新构建镜像
docker build -t opsagent:latest .

# 3. 加载到 kind
kind load docker-image opsagent:latest --name opsagent-dev

# 4. 重启 deployment
kubectl rollout restart deployment/opsagent -n ops-system

# 5. 查看新日志
kubectl logs -f -n ops-system -l app=opsagent

# 或使用一键脚本
./scripts/deploy-local.sh
```

### 使用 Self-Hosted Runner + Kind

这是最强大的组合！

```bash
# 1. 在本地安装 self-hosted runner
# (参考 QUICK_START_SELF_HOSTED.md)

# 2. Runner 会自动:
#    - 检测代码变更
#    - 构建 Docker 镜像
#    - 加载到 kind 集群
#    - 部署到 ops-system namespace
#    - 运行健康检查

# 3. 你只需要:
git add .
git commit -m "Update feature"
git push origin main

# 4. 在 GitHub Actions 查看部署进度
```

## 📊 访问应用的多种方式

### 方式 1: Port Forward（推荐用于开发）

```bash
# 转发 API 端口
kubectl port-forward -n ops-system svc/opsagent 18080:80

# 在另一个终端访问
curl http://localhost:18080/health
curl http://localhost:18080/api/issues

# 转发 Metrics 端口
kubectl port-forward -n ops-system svc/opsagent 9090:9090
curl http://localhost:9090/metrics
```

### 方式 2: NodePort Service

修改 `deploy/k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: opsagent
  namespace: ops-system
spec:
  type: NodePort  # 改为 NodePort
  ports:
    - name: http
      port: 80
      targetPort: 18080
      nodePort: 30080  # 固定端口
    - name: metrics
      port: 9090
      targetPort: 9090
      nodePort: 30090
  selector:
    app: opsagent
```

应用后访问：

```bash
# API
curl http://localhost:30080/health

# Metrics
curl http://localhost:30090/metrics
```

### 方式 3: LoadBalancer（使用 MetalLB）

```bash
# 安装 MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml

# 配置 IP 地址池
cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: example
  namespace: metallb-system
spec:
  addresses:
  - 172.18.0.100-172.18.0.110
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: empty
  namespace: metallb-system
EOF

# 修改 Service 为 LoadBalancer 类型
# 然后获取外部 IP
kubectl get svc -n ops-system
```

### 方式 4: Ingress

```bash
# 安装 Nginx Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# 等待 Ingress Controller 就绪
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# 创建 Ingress 资源
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: opsagent
  namespace: ops-system
spec:
  rules:
  - host: opsagent.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: opsagent
            port:
              number: 80
EOF

# 添加到 /etc/hosts
echo "127.0.0.1 opsagent.local" | sudo tee -a /etc/hosts

# 访问
curl http://opsagent.local/health
```

## 🔧 常用命令

### 集群管理

```bash
# 查看所有 kind 集群
kind get clusters

# 删除集群
kind delete cluster --name opsagent-dev

# 导出 kubeconfig
kind get kubeconfig --name opsagent-dev > ~/.kube/kind-config

# 查看集群节点
kubectl get nodes

# 查看集群信息
kubectl cluster-info
```

### 镜像管理

```bash
# 加载本地镜像到 kind
kind load docker-image opsagent:latest --name opsagent-dev

# 加载镜像 tar 文件
docker save opsagent:latest > opsagent.tar
kind load image-archive opsagent.tar --name opsagent-dev

# 在 kind 节点中查看镜像
docker exec -it opsagent-dev-control-plane crictl images
```

### 应用调试

```bash
# 查看所有资源
kubectl get all -n ops-system

# 查看 Pod 详情
kubectl describe pod -n ops-system -l app=opsagent

# 查看日志
kubectl logs -f -n ops-system -l app=opsagent

# 进入 Pod
kubectl exec -it -n ops-system deployment/opsagent -- /bin/bash

# 查看事件
kubectl get events -n ops-system --sort-by='.lastTimestamp'

# 查看资源使用
kubectl top pods -n ops-system
kubectl top nodes
```

### 快速重部署

```bash
# 一键重新部署
docker build -t opsagent:latest . && \
kind load docker-image opsagent:latest --name opsagent-dev && \
kubectl rollout restart deployment/opsagent -n ops-system && \
kubectl rollout status deployment/opsagent -n ops-system

# 或使用脚本
./scripts/deploy-local.sh
```

## 📝 本地部署脚本

我已经创建了 `scripts/deploy-local.sh` 脚本，包含所有常用操作：

```bash
# 查看帮助
./scripts/deploy-local.sh --help

# 创建集群
./scripts/deploy-local.sh create

# 部署应用
./scripts/deploy-local.sh deploy

# 快速重部署（重新构建 + 部署）
./scripts/deploy-local.sh redeploy

# 查看状态
./scripts/deploy-local.sh status

# 查看日志
./scripts/deploy-local.sh logs

# 端口转发
./scripts/deploy-local.sh port-forward

# 删除集群
./scripts/deploy-local.sh delete
```

## ⚠️ 常见问题

### 问题 1: ImagePullBackOff

**原因**: 镜像没有加载到 kind 集群

**解决**:
```bash
# 确保镜像存在
docker images | grep opsagent

# 加载到 kind
kind load docker-image opsagent:latest --name opsagent-dev

# 确保 imagePullPolicy 设置为 Never 或 IfNotPresent
```

### 问题 2: Pod CrashLoopBackOff

**解决**:
```bash
# 查看日志
kubectl logs -n ops-system -l app=opsagent

# 查看详细信息
kubectl describe pod -n ops-system -l app=opsagent

# 检查配置
kubectl get configmap opsagent-config -n ops-system -o yaml
```

### 问题 3: 无法访问应用

**解决**:
```bash
# 确认 Service 存在
kubectl get svc -n ops-system

# 确认 Pod 运行
kubectl get pods -n ops-system

# 测试 Pod 内部连接
POD_NAME=$(kubectl get pods -n ops-system -l app=opsagent -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n ops-system $POD_NAME -- curl http://localhost:18080/health

# 使用 port-forward
kubectl port-forward -n ops-system svc/opsagent 18080:80
```

### 问题 4: Docker 资源不足

**解决**:
```bash
# 增加 Docker Desktop 资源
# Docker Desktop → Preferences → Resources
# 推荐: 4 CPUs, 8GB Memory, 50GB Disk

# 清理 Docker 资源
docker system prune -a -f

# 清理未使用的 kind 集群
kind delete cluster --name old-cluster
```

### 问题 5: 集群创建失败

**解决**:
```bash
# 删除旧集群
kind delete cluster --name opsagent-dev

# 清理 Docker 网络
docker network prune -f

# 重新创建
kind create cluster --config kind-config.yaml

# 如果还是失败，尝试不使用配置文件
kind create cluster --name opsagent-dev
```

## 💡 最佳实践

### 1. 使用本地镜像

```bash
# 始终设置 imagePullPolicy: Never 或 IfNotPresent
# 这样可以避免尝试从远程拉取镜像
```

### 2. 快速迭代

```bash
# 创建 alias 简化命令
alias k='kubectl'
alias kgp='kubectl get pods -n ops-system'
alias klog='kubectl logs -f -n ops-system -l app=opsagent'
alias kredeploy='docker build -t opsagent:latest . && kind load docker-image opsagent:latest --name opsagent-dev && kubectl rollout restart deployment/opsagent -n ops-system'
```

### 3. 保留开发数据

```bash
# 使用 PersistentVolume 保存数据
# 即使删除 Pod，数据也不会丢失
```

### 4. 多集群管理

```bash
# 为不同功能创建不同集群
kind create cluster --name opsagent-dev      # 开发
kind create cluster --name opsagent-test     # 测试
kind create cluster --name opsagent-demo     # 演示

# 切换集群
kubectl config use-context kind-opsagent-dev
kubectl config use-context kind-opsagent-test
```

### 5. 资源监控

```bash
# 安装 k9s（可选但强烈推荐）
brew install derailed/k9s/k9s

# 启动 k9s
k9s -n ops-system

# k9s 提供了友好的 TUI 界面来管理集群
```

## 🎓 学习资源

- [Kind 官方文档](https://kind.sigs.k8s.io/)
- [Kind 快速开始](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [Kind 配置文档](https://kind.sigs.k8s.io/docs/user/configuration/)

## 📊 Kind vs 其他本地 K8s 方案

| 特性 | Kind | Minikube | k3d | Docker Desktop K8s |
|------|------|----------|-----|-------------------|
| 速度 | ⚡ 快 | 中等 | ⚡⚡ 很快 | 快 |
| 资源占用 | 低 | 中等 | 低 | 中等 |
| 多节点支持 | ✅ | ✅ | ✅ | ❌ |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| CI/CD 集成 | ✅ 优秀 | ✅ | ✅ | ❌ |

**推荐使用 Kind 的原因**:
- 专为 CI/CD 和测试设计
- 启动速度快
- 资源占用少
- 支持多节点
- 与 GitHub Actions 集成完美

---

**快速开始**: 运行 `./scripts/deploy-local.sh create` 立即开始！ 🚀
