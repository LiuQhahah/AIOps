# OpsAgent Helm Chart 部署指南

使用 Helm 将 OpsAgent 部署到任何 Kubernetes 环境。

## 📋 目录

- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [配置选项](#配置选项)
- [部署到不同环境](#部署到不同环境)
- [升级和回滚](#升级和回滚)
- [卸载](#卸载)
- [故障排查](#故障排查)

## 🎯 前置要求

### 必需

- **Kubernetes 集群** v1.19+
- **Helm** v3.8+
- **kubectl** 已配置并能访问集群

### 验证环境

```bash
# 检查 Kubernetes 连接
kubectl cluster-info

# 检查 Helm 版本
helm version

# 检查当前 context
kubectl config current-context
```

## ⚡ 快速开始

### 1. 基本安装（推荐用于测试）

```bash
# 从本地 Chart 安装
helm install opsagent ./helm/opsagent

# 或指定 namespace
helm install opsagent ./helm/opsagent --namespace ops-system --create-namespace
```

### 2. 自定义安装

```bash
# 使用自定义 values 文件
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --values custom-values.yaml
```

### 3. 验证安装

```bash
# 检查部署状态
helm status opsagent -n ops-system

# 查看 pods
kubectl get pods -n ops-system

# 查看日志
kubectl logs -f -n ops-system -l app=opsagent
```

## 🎨 配置选项

### 方式 1: 使用 --set 参数

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --set image.repository=your-registry/opsagent \
  --set image.tag=1.0.0 \
  --set config.detection.interval=600 \
  --set config.remediation.enabled=false
```

### 方式 2: 使用自定义 values 文件（推荐）

创建 `my-values.yaml`:

```yaml
# 基本配置
replicaCount: 1

# 镜像配置
image:
  repository: your-registry/opsagent
  tag: "1.0.0"
  pullPolicy: IfNotPresent

# 应用配置
config:
  detection:
    interval: 300  # 5 分钟

  remediation:
    enabled: false  # 仅检测，不修复
    dry_run: true

  logging:
    level: INFO
    format: json

# 资源配置
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 512Mi
```

安装：

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --values my-values.yaml
```

## 🌍 部署到不同环境

### 场景 1: Kind 本地集群

```yaml
# values-kind.yaml
image:
  repository: opsagent
  tag: latest
  pullPolicy: Never  # 使用本地镜像

config:
  k8s:
    in_cluster: true

  detection:
    interval: 60  # 更短的间隔用于测试

  remediation:
    enabled: false
```

部署：

```bash
# 1. 构建并加载镜像到 Kind
docker build -t opsagent:latest .
kind load docker-image opsagent:latest --name opsagent-dev

# 2. 使用 Helm 安装
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --values values-kind.yaml
```

### 场景 2: 开发环境

```yaml
# values-dev.yaml
replicaCount: 1

image:
  repository: your-registry/opsagent
  tag: dev
  pullPolicy: Always

config:
  detection:
    interval: 300

  remediation:
    enabled: false  # 开发环境只检测

  logging:
    level: DEBUG  # 详细日志

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

### 场景 3: 生产环境

```yaml
# values-prod.yaml
replicaCount: 1

image:
  repository: your-registry/opsagent
  tag: "1.0.0"  # 使用固定版本
  pullPolicy: IfNotPresent

# 使用现有 secret
existingSecret: opsagent-secrets-prod

config:
  k8s:
    in_cluster: true

  detection:
    interval: 300

  remediation:
    enabled: true  # 启用自动修复
    dry_run: false  # 实际执行修复

  logging:
    level: INFO
    format: json

  # AWS 集成
  aws:
    enabled: true
    region: us-east-1
    resources:
      rds:
        enabled: true
      kinesis:
        enabled: true

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 1Gi

# 监控
monitoring:
  serviceMonitor:
    enabled: true
    interval: 30s

# Ingress
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: opsagent.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: opsagent-tls
      hosts:
        - opsagent.example.com

# Pod Disruption Budget
podDisruptionBudget:
  enabled: true
  minAvailable: 1

# 资源限制
nodeSelector:
  node-role: ops-tools

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: opsagent
          topologyKey: kubernetes.io/hostname
```

### 场景 4: 启用 AWS 监控

```yaml
# values-aws.yaml
config:
  aws:
    enabled: true
    region: us-east-1
    resources:
      rds:
        enabled: true
      kinesis:
        enabled: true

# 配置 AWS 凭证
secrets:
  create: true
  aws:
    accessKeyId: "AKIAIOSFODNN7EXAMPLE"
    secretAccessKey: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

或使用 IRSA (IAM Roles for Service Accounts):

```yaml
# values-aws-irsa.yaml
serviceAccount:
  create: true
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/opsagent-role

config:
  aws:
    enabled: true
    region: us-east-1
    resources:
      rds:
        enabled: true
```

## 🔄 升级和回滚

### 升级 Chart

```bash
# 升级到新版本
helm upgrade opsagent ./helm/opsagent \
  --namespace ops-system \
  --values my-values.yaml

# 查看升级历史
helm history opsagent -n ops-system
```

### 回滚

```bash
# 回滚到上一个版本
helm rollback opsagent -n ops-system

# 回滚到特定版本
helm rollback opsagent 2 -n ops-system
```

### 检查升级前的差异

```bash
# 查看会发生什么变化
helm diff upgrade opsagent ./helm/opsagent \
  --namespace ops-system \
  --values my-values.yaml
```

## 🗑️ 卸载

```bash
# 卸载 release
helm uninstall opsagent -n ops-system

# 删除 namespace（可选）
kubectl delete namespace ops-system
```

## 🔧 高级配置

### 使用外部 Secret

```bash
# 1. 创建 Secret
kubectl create secret generic opsagent-secrets \
  --from-literal=aws-access-key-id=YOUR_KEY \
  --from-literal=aws-secret-access-key=YOUR_SECRET \
  --namespace=ops-system

# 2. 在 values 中引用
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --set existingSecret=opsagent-secrets
```

### 配置 Ingress

```yaml
# values.yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
  hosts:
    - host: opsagent.local
      paths:
        - path: /
          pathType: Prefix
```

### 启用 Prometheus 监控

```yaml
# values.yaml
monitoring:
  serviceMonitor:
    enabled: true
    interval: 30s
    scrapeTimeout: 10s
    labels:
      prometheus: kube-prometheus
```

### 自定义资源限制

```yaml
# values.yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 512Mi
```

### 配置节点选择

```yaml
# values.yaml
nodeSelector:
  disktype: ssd
  node-role: ops

tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "ops"
    effect: "NoSchedule"

affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: node-role
              operator: In
              values:
                - ops-tools
```

## 📊 Helm 命令速查

### 安装和升级

```bash
# 安装
helm install opsagent ./helm/opsagent -n ops-system --create-namespace

# 升级
helm upgrade opsagent ./helm/opsagent -n ops-system

# 安装或升级（如果不存在则安装，存在则升级）
helm upgrade --install opsagent ./helm/opsagent -n ops-system --create-namespace

# Dry-run（查看会生成什么资源）
helm install opsagent ./helm/opsagent --dry-run --debug
```

### 查看和调试

```bash
# 查看 release 状态
helm status opsagent -n ops-system

# 查看 release 的值
helm get values opsagent -n ops-system

# 查看所有配置（包括默认值）
helm get values opsagent -n ops-system --all

# 查看生成的 manifest
helm get manifest opsagent -n ops-system

# 查看历史
helm history opsagent -n ops-system

# 验证 Chart
helm lint ./helm/opsagent

# 模板渲染测试
helm template opsagent ./helm/opsagent --debug
```

### 卸载和清理

```bash
# 卸载
helm uninstall opsagent -n ops-system

# 卸载并保留历史
helm uninstall opsagent -n ops-system --keep-history
```

## 🐛 故障排查

### 问题 1: Chart 无法安装

```bash
# 验证 Chart 语法
helm lint ./helm/opsagent

# 查看详细错误
helm install opsagent ./helm/opsagent --debug --dry-run
```

### 问题 2: Pod 无法启动

```bash
# 查看 Pod 状态
kubectl get pods -n ops-system

# 查看 Pod 详情
kubectl describe pod -n ops-system -l app=opsagent

# 查看日志
kubectl logs -n ops-system -l app=opsagent
```

### 问题 3: 配置未生效

```bash
# 查看实际使用的配置
helm get values opsagent -n ops-system --all

# 查看 ConfigMap
kubectl get configmap -n ops-system
kubectl describe configmap opsagent-config -n ops-system
```

### 问题 4: 镜像拉取失败

```yaml
# 配置 imagePullSecrets
imagePullSecrets:
  - name: regcred

# 创建 imagePullSecret
kubectl create secret docker-registry regcred \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password \
  --namespace=ops-system
```

### 问题 5: RBAC 权限错误

```bash
# 检查 ServiceAccount
kubectl get sa -n ops-system

# 检查 ClusterRole
kubectl get clusterrole | grep opsagent

# 检查 ClusterRoleBinding
kubectl get clusterrolebinding | grep opsagent

# 查看详细信息
kubectl describe clusterrole opsagent-reader
```

## 📝 最佳实践

### 1. 版本管理

```yaml
# 始终指定确切的镜像版本（生产环境）
image:
  tag: "1.0.0"  # 不要使用 latest

# 或使用 Chart AppVersion
image:
  tag: ""  # 留空使用 Chart.yaml 中的 appVersion
```

### 2. 使用 Values 文件管理配置

```bash
# 为不同环境创建不同的 values 文件
values/
  ├── values-dev.yaml
  ├── values-staging.yaml
  └── values-prod.yaml

# 部署时引用
helm install opsagent ./helm/opsagent -f values/values-prod.yaml
```

### 3. Secret 管理

```bash
# 使用 Sealed Secrets 或 External Secrets
# 不要将敏感信息提交到 Git

# 或使用云提供商的密钥管理服务
# AWS: Secrets Manager + External Secrets Operator
# Azure: Key Vault + External Secrets Operator
```

### 4. 资源限制

```yaml
# 始终设置资源限制
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 512Mi
```

### 5. 健康检查

```yaml
# 配置适当的探针
livenessProbe:
  httpGet:
    path: /health
    port: 18080
  initialDelaySeconds: 30
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 18080
  initialDelaySeconds: 10
  periodSeconds: 10
```

## 🎯 完整部署示例

### 示例 1: 部署到 Kind 集群

```bash
#!/bin/bash
# deploy-to-kind.sh

# 1. 创建 Kind 集群
kind create cluster --name opsagent-dev

# 2. 构建镜像
docker build -t opsagent:latest .

# 3. 加载镜像到 Kind
kind load docker-image opsagent:latest --name opsagent-dev

# 4. 使用 Helm 部署
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --set image.pullPolicy=Never \
  --set config.detection.interval=60

# 5. 验证
kubectl get pods -n ops-system
helm status opsagent -n ops-system
```

### 示例 2: 部署到生产环境

```bash
#!/bin/bash
# deploy-to-prod.sh

# 1. 设置变量
NAMESPACE="ops-system"
RELEASE_NAME="opsagent"
VALUES_FILE="values/values-prod.yaml"

# 2. 验证 Chart
helm lint ./helm/opsagent

# 3. 模拟部署（Dry-run）
helm upgrade --install $RELEASE_NAME ./helm/opsagent \
  --namespace $NAMESPACE \
  --create-namespace \
  --values $VALUES_FILE \
  --dry-run --debug

# 4. 确认后执行实际部署
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  helm upgrade --install $RELEASE_NAME ./helm/opsagent \
    --namespace $NAMESPACE \
    --create-namespace \
    --values $VALUES_FILE \
    --wait \
    --timeout 5m
fi

# 5. 验证部署
kubectl rollout status deployment/opsagent -n $NAMESPACE
helm status $RELEASE_NAME -n $NAMESPACE
```

## 📚 相关文档

- [Helm 官方文档](https://helm.sh/docs/)
- [Kubernetes 部署文档](KUBERNETES_DEPLOYMENT.md)
- [Kind 本地部署](KIND_LOCAL_SETUP.md)
- [CI/CD 文档](CICD_README.md)

---

**准备好了吗？** 使用以下命令开始部署：

```bash
helm install opsagent ./helm/opsagent --namespace ops-system --create-namespace
```

🚀 Happy Helming!
