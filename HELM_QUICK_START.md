# Helm 快速开始 🚀

3 分钟使用 Helm 部署 OpsAgent 到任何 Kubernetes 环境！

## ⚡ 超快速开始

```bash
# 一行命令部署
helm install opsagent ./helm/opsagent --namespace ops-system --create-namespace

# 等待部署完成
kubectl rollout status deployment/opsagent -n ops-system

# 查看运行状态
kubectl get pods -n ops-system

# 访问应用
kubectl port-forward -n ops-system svc/opsagent 18080:80
# 然后访问 http://localhost:18080/health
```

就这么简单！✨

## 🎯 不同场景快速部署

### 场景 1: Kind 本地集群

```bash
# 1. 构建并加载镜像
docker build -t opsagent:latest .
kind load docker-image opsagent:latest --name opsagent-dev

# 2. 部署
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --set image.pullPolicy=Never
```

### 场景 2: 使用远程镜像仓库

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --set image.repository=your-registry/opsagent \
  --set image.tag=1.0.0
```

### 场景 3: 启用自动修复（生产环境）

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --set config.remediation.enabled=true \
  --set config.remediation.dry_run=false
```

### 场景 4: 自定义检测间隔

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --set config.detection.interval=600  # 10分钟
```

## 🔄 常用操作

### 查看状态

```bash
# 查看 release 状态
helm status opsagent -n ops-system

# 查看 pods
kubectl get pods -n ops-system

# 查看日志
kubectl logs -f -n ops-system -l app=opsagent
```

### 升级配置

```bash
# 修改配置后升级
helm upgrade opsagent ./helm/opsagent \
  --namespace ops-system \
  --set config.detection.interval=300
```

### 回滚

```bash
# 回滚到上一个版本
helm rollback opsagent -n ops-system
```

### 卸载

```bash
# 卸载 OpsAgent
helm uninstall opsagent -n ops-system

# 删除 namespace (可选)
kubectl delete namespace ops-system
```

## 📝 使用自定义配置文件

创建 `my-values.yaml`:

```yaml
# 基本配置
image:
  repository: opsagent
  tag: latest
  pullPolicy: Never  # Kind 本地镜像

config:
  detection:
    interval: 60  # 1分钟（用于测试）

  remediation:
    enabled: false  # 仅检测

  logging:
    level: DEBUG  # 详细日志

resources:
  requests:
    cpu: 100m
    memory: 128Mi
```

使用：

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --values my-values.yaml
```

## 🎨 实用配置模板

### 开发环境配置

```yaml
# values-dev.yaml
replicaCount: 1

image:
  repository: opsagent
  tag: dev
  pullPolicy: Always

config:
  detection:
    interval: 60
  remediation:
    enabled: false
  logging:
    level: DEBUG

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

### 生产环境配置

```yaml
# values-prod.yaml
replicaCount: 1

image:
  repository: your-registry/opsagent
  tag: "1.0.0"
  pullPolicy: IfNotPresent

config:
  detection:
    interval: 300
  remediation:
    enabled: true
    dry_run: false
  logging:
    level: INFO
    format: json

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 1Gi

monitoring:
  serviceMonitor:
    enabled: true
```

## 🔧 故障排查

### 问题：Pod 无法启动

```bash
# 查看 Pod 状态
kubectl describe pod -n ops-system -l app=opsagent

# 查看日志
kubectl logs -n ops-system -l app=opsagent
```

### 问题：镜像拉取失败

```bash
# 检查镜像设置
helm get values opsagent -n ops-system

# 如果使用 Kind，确保镜像已加载
kind load docker-image opsagent:latest --name opsagent-dev
```

### 问题：配置未生效

```bash
# 查看实际配置
helm get values opsagent -n ops-system --all

# 查看 ConfigMap
kubectl get cm opsagent-config -n ops-system -o yaml
```

## 💡 有用的别名

添加到 `~/.bashrc` 或 `~/.zshrc`:

```bash
# Helm 别名
alias h='helm'
alias hl='helm list'
alias hi='helm install'
alias hu='helm upgrade'
alias hd='helm uninstall'

# Helm + kubectl 组合
alias kh='kubectl --namespace=ops-system'
alias khp='kubectl get pods --namespace=ops-system'
alias khl='kubectl logs -f --namespace=ops-system -l app=opsagent'
```

使用：

```bash
hi opsagent ./helm/opsagent --namespace ops-system --create-namespace
khp  # 查看 pods
khl  # 查看日志
```

## 📊 Helm 命令速查

```bash
# 安装
helm install opsagent ./helm/opsagent -n ops-system --create-namespace

# 升级
helm upgrade opsagent ./helm/opsagent -n ops-system

# 安装或升级
helm upgrade --install opsagent ./helm/opsagent -n ops-system --create-namespace

# 查看状态
helm status opsagent -n ops-system

# 查看历史
helm history opsagent -n ops-system

# 回滚
helm rollback opsagent -n ops-system

# 卸载
helm uninstall opsagent -n ops-system

# 测试
helm lint ./helm/opsagent
helm template opsagent ./helm/opsagent --debug
helm install opsagent ./helm/opsagent --dry-run --debug
```

## 🎯 完整部署脚本

创建 `deploy-helm.sh`:

```bash
#!/bin/bash
set -e

# 配置
RELEASE_NAME="opsagent"
NAMESPACE="ops-system"
CHART_PATH="./helm/opsagent"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying OpsAgent with Helm...${NC}"

# 1. 验证 Chart
echo -e "${BLUE}📋 Validating Chart...${NC}"
helm lint $CHART_PATH

# 2. 部署
echo -e "${BLUE}📦 Installing/Upgrading...${NC}"
helm upgrade --install $RELEASE_NAME $CHART_PATH \
  --namespace $NAMESPACE \
  --create-namespace \
  --wait \
  --timeout 5m

# 3. 验证
echo -e "${BLUE}✅ Verifying deployment...${NC}"
kubectl rollout status deployment/$RELEASE_NAME -n $NAMESPACE

# 4. 显示状态
echo -e "${GREEN}✅ Deployment successful!${NC}"
helm status $RELEASE_NAME -n $NAMESPACE

# 5. 显示访问方式
echo ""
echo -e "${BLUE}📍 Access the application:${NC}"
echo "  kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME 18080:80"
echo ""
echo -e "${BLUE}📝 View logs:${NC}"
echo "  kubectl logs -f -n $NAMESPACE -l app=opsagent"
```

使用：

```bash
chmod +x deploy-helm.sh
./deploy-helm.sh
```

## 🎓 下一步

- 📖 阅读 [完整 Helm 文档](HELM_DEPLOYMENT.md)
- 🔧 查看 [values.yaml](helm/opsagent/values.yaml) 所有配置选项
- 📚 了解 [Kubernetes 部署细节](KUBERNETES_DEPLOYMENT.md)
- 🚀 配置 [CI/CD 自动部署](CICD_README.md)

---

**现在就开始：**

```bash
helm install opsagent ./helm/opsagent --namespace ops-system --create-namespace
```

🎉 Happy Helming!
