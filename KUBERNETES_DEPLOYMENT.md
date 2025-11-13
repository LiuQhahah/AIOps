# OpsAgent Kubernetes 部署指南

## 📋 目录

- [架构概览](#架构概览)
- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [部署步骤](#部署步骤)
- [验证部署](#验证部署)
- [故障排查](#故障排查)
- [卸载](#卸载)

## 架构概览

OpsAgent 在 Kubernetes 集群中的部署架构：

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes 集群                       │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Namespace: ops-system                  │ │
│  │                                                     │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │         Deployment: opsagent                 │  │ │
│  │  │                                              │  │ │
│  │  │  ┌────────────────────────────────────────┐ │  │ │
│  │  │  │  Pod: opsagent-xxxxx                   │ │  │ │
│  │  │  │                                        │ │  │ │
│  │  │  │  - API Server (18080)                  │ │  │ │
│  │  │  │  - Metrics (9090)                      │ │  │ │
│  │  │  │  - Detection Engine                    │ │  │ │
│  │  │  │                                        │ │  │ │
│  │  │  │  使用 ServiceAccount: opsagent         │ │  │ │
│  │  │  └────────────────────────────────────────┘ │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  │                                                     │ │
│  │  Service: opsagent                                  │ │
│  │    - ClusterIP                                      │ │
│  │    - Port 80 -> 18080 (API)                         │ │
│  │    - Port 9090 (Metrics)                            │ │
│  │                                                     │ │
│  │  ConfigMap: opsagent-config                         │ │
│  │  Secret: opsagent-secrets (可选)                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  RBAC:                                                   │
│  - ServiceAccount: opsagent                              │
│  - ClusterRole: opsagent-reader                          │
│  - ClusterRoleBinding: opsagent-reader-binding           │
│                                                          │
│  权限:                                                   │
│  - 读取 Deployments, StatefulSets, DaemonSets            │
│  - 读取 Pods, Services, ConfigMaps                       │
│  - 读取 Namespaces, Nodes                                │
│  - 读取 Metrics (可选)                                   │
└─────────────────────────────────────────────────────────┘
```

## 前置要求

### 必需

- ✅ **Kubernetes 集群** (v1.19+)
- ✅ **kubectl** 已安装并配置
- ✅ **Docker** (用于构建镜像)
- ✅ 集群管理员权限 (创建 ClusterRole)

### 可选

- **镜像仓库** (如 Docker Hub, Harbor, ECR)
- **Prometheus** (用于监控指标)
- **Ingress Controller** (如需外部访问)

### 资源要求

| 资源 | 请求 | 限制 |
|------|------|------|
| CPU | 200m | 1000m |
| Memory | 256Mi | 512Mi |

## 快速开始

### 1. 构建镜像

```bash
# 进入项目目录
cd AIOps

# 构建 Docker 镜像
docker build -t opsagent:latest .

# (可选) 推送到镜像仓库
docker tag opsagent:latest your-registry/opsagent:latest
docker push your-registry/opsagent:latest
```

### 2. 一键部署

```bash
cd deploy/k8s

# 安装 OpsAgent
./deploy.sh install

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs
```

就这么简单！OpsAgent 现在已经在集群中运行了。

## 详细配置

### 配置 ConfigMap

编辑 `deploy/k8s/configmap.yaml` 来自定义检测行为：

```yaml
data:
  config.yaml: |
    k8s:
      in_cluster: true  # 必须设为 true

    detection:
      interval: 300  # 检测间隔（秒）

    remediation:
      enabled: false  # 建议先设为 false，只检测不修复

    logging:
      level: INFO  # DEBUG, INFO, WARNING, ERROR
```

### 配置 Secret（可选）

如果需要访问 AWS/Azure 或发送通知，创建 Secret：

```bash
# 创建 Secret
kubectl create secret generic opsagent-secrets \
  --from-literal=aws-access-key-id=YOUR_KEY \
  --from-literal=aws-secret-access-key=YOUR_SECRET \
  --from-literal=github-token=YOUR_TOKEN \
  --namespace=ops-system
```

或者基于模板文件创建：

```bash
# 复制模板
cp secret-template.yaml secret.yaml

# 编辑 secret.yaml，填写 base64 编码的值
# echo -n "your-value" | base64

# 应用
kubectl apply -f secret.yaml
```

### 修改 Deployment 镜像

编辑 `deploy/k8s/deployment.yaml`：

```yaml
spec:
  template:
    spec:
      containers:
        - name: opsagent
          image: your-registry/opsagent:v1.0.0  # 修改为你的镜像
          imagePullPolicy: Always
```

### 调整资源配额

根据集群大小调整资源：

```yaml
resources:
  requests:
    cpu: 200m      # 小集群: 100m, 大集群: 500m
    memory: 256Mi  # 小集群: 128Mi, 大集群: 512Mi
  limits:
    cpu: 1000m
    memory: 512Mi
```

## 部署步骤

### 方式 1: 使用自动化脚本（推荐）

```bash
cd deploy/k8s

# 1. 安装
./deploy.sh install

# 2. 查看状态
./deploy.sh status

# 3. 查看日志
./deploy.sh logs

# 4. 端口转发到本地
./deploy.sh port-forward 8080
# 访问 http://localhost:8080
```

### 方式 2: 手动部署

```bash
cd deploy/k8s

# 1. 创建命名空间
kubectl apply -f namespace.yaml

# 2. 创建 RBAC
kubectl apply -f rbac.yaml

# 3. 创建 ConfigMap
kubectl apply -f configmap.yaml

# 4. 创建 Secret（如果需要）
kubectl apply -f secret.yaml

# 5. 创建 Deployment
kubectl apply -f deployment.yaml

# 6. 创建 Service
kubectl apply -f service.yaml

# 7. 等待就绪
kubectl rollout status deployment/opsagent -n ops-system
```

## 验证部署

### 1. 检查 Pod 状态

```bash
kubectl get pods -n ops-system

# 期望输出:
# NAME                        READY   STATUS    RESTARTS   AGE
# opsagent-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

### 2. 查看日志

```bash
kubectl logs -f deployment/opsagent -n ops-system

# 期望看到:
# INFO Starting OpsAgent...
# INFO Detection scheduler started
# INFO K8s detectors initialized
```

### 3. 检查健康状态

```bash
kubectl exec -it deployment/opsagent -n ops-system -- curl localhost:18080/health

# 期望输出:
# {"status": "healthy"}
```

### 4. 访问 API

```bash
# 端口转发
kubectl port-forward -n ops-system deployment/opsagent 18080:18080

# 在另一个终端访问
curl http://localhost:18080/health
```

### 5. 检查 Metrics

```bash
kubectl port-forward -n ops-system svc/opsagent 9090:9090

# 访问 Prometheus metrics
curl http://localhost:9090/metrics
```

### 6. 验证检测功能

查看日志中是否有检测结果：

```bash
kubectl logs deployment/opsagent -n ops-system | grep "issues_found"

# 期望看到类似:
# INFO Detection cycle completed total_issues=5
```

## 高级配置

### 启用 Ingress（外部访问）

创建 `ingress.yaml`：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: opsagent
  namespace: ops-system
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: opsagent.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: opsagent
                port:
                  number: 80
```

应用：

```bash
kubectl apply -f ingress.yaml
```

### 配置 HPA（水平自动扩缩容）

创建 `hpa.yaml`：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: opsagent
  namespace: ops-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: opsagent
  minReplicas: 1
  maxReplicas: 3
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

**注意**: 由于 OpsAgent 使用定时任务，建议保持单实例运行避免重复检测。

### 集成 Prometheus

如果使用 Prometheus Operator，Service 已包含 ServiceMonitor：

```bash
kubectl get servicemonitor -n ops-system
```

查看 Prometheus Target：

```
http://prometheus-url/targets
# 应该能看到 opsagent/metrics 端点
```

## 故障排查

### Pod 无法启动

```bash
# 查看 Pod 事件
kubectl describe pod -l app=opsagent -n ops-system

# 常见问题:
# 1. 镜像拉取失败
#    - 检查镜像名称是否正确
#    - 检查 imagePullSecrets 配置

# 2. 权限不足
#    - 确认 RBAC 已正确配置
#    - kubectl get clusterrolebinding opsagent-reader-binding

# 3. 配置错误
#    - 检查 ConfigMap: kubectl get cm opsagent-config -n ops-system -o yaml
```

### 检测器无法访问 K8s API

```bash
# 检查 ServiceAccount
kubectl get sa opsagent -n ops-system

# 检查 ClusterRole 权限
kubectl describe clusterrole opsagent-reader

# 检查绑定
kubectl get clusterrolebinding opsagent-reader-binding -o yaml
```

### 查看详细日志

```bash
# 实时日志
kubectl logs -f deployment/opsagent -n ops-system

# 之前的日志（如果 Pod 重启过）
kubectl logs deployment/opsagent -n ops-system --previous

# 导出日志到文件
kubectl logs deployment/opsagent -n ops-system > opsagent.log
```

### 进入 Pod 调试

```bash
# 进入 Pod
kubectl exec -it deployment/opsagent -n ops-system -- /bin/bash

# 手动运行检测器
cd /app
python -m src.main --config /app/config/config.yaml

# 检查配置文件
cat /app/config/config.yaml

# 测试 K8s 连接
python -c "from kubernetes import client, config; config.load_incluster_config(); print('OK')"
```

### 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `ImagePullBackOff` | 镜像不存在或无权限 | 检查镜像名称，配置 imagePullSecrets |
| `CrashLoopBackOff` | 应用启动失败 | 查看日志，检查配置文件 |
| `Forbidden: User "system:serviceaccount:ops-system:opsagent" cannot list resource` | RBAC 权限不足 | 检查 ClusterRole 和 ClusterRoleBinding |
| `Failed to load kube config` | 配置错误 | 确认 `in_cluster: true` |

## 运维操作

### 更新配置

```bash
# 1. 修改 ConfigMap
kubectl edit configmap opsagent-config -n ops-system

# 2. 重启 Deployment
kubectl rollout restart deployment/opsagent -n ops-system

# 3. 等待就绪
kubectl rollout status deployment/opsagent -n ops-system
```

### 升级版本

```bash
# 方式 1: 使用脚本
cd deploy/k8s
./deploy.sh upgrade

# 方式 2: 手动升级
kubectl set image deployment/opsagent \
  opsagent=your-registry/opsagent:v1.1.0 \
  -n ops-system
```

### 扩缩容（不推荐）

```bash
# 扩展到 2 个副本（不推荐，可能导致重复检测）
kubectl scale deployment/opsagent --replicas=2 -n ops-system

# 缩减到 1 个副本
kubectl scale deployment/opsagent --replicas=1 -n ops-system
```

### 暂停检测

```bash
# 缩容到 0
kubectl scale deployment/opsagent --replicas=0 -n ops-system

# 恢复
kubectl scale deployment/opsagent --replicas=1 -n ops-system
```

## 卸载

### 使用脚本卸载

```bash
cd deploy/k8s
./deploy.sh uninstall

# 按提示选择是否删除 Secret 和 Namespace
```

### 手动卸载

```bash
# 删除所有资源
kubectl delete -f deploy/k8s/service.yaml
kubectl delete -f deploy/k8s/deployment.yaml
kubectl delete -f deploy/k8s/configmap.yaml
kubectl delete -f deploy/k8s/rbac.yaml
kubectl delete namespace ops-system
```

### 清理镜像

```bash
# 本地镜像
docker rmi opsagent:latest

# 远程镜像（从仓库删除）
# 根据你的镜像仓库操作
```

## 监控和告警

### Prometheus 指标

OpsAgent 暴露以下指标：

- `opsagent_detection_runs_total` - 检测运行次数
- `opsagent_issues_found_total` - 发现的问题数量
- `opsagent_issues_by_severity` - 按严重程度分类的问题
- `opsagent_detection_duration_seconds` - 检测耗时

### Grafana Dashboard

创建 Grafana Dashboard 查询示例：

```promql
# 每小时发现的问题数
rate(opsagent_issues_found_total[1h])

# 按严重程度分类
sum by (severity) (opsagent_issues_by_severity)

# 平均检测耗时
avg(opsagent_detection_duration_seconds)
```

## 最佳实践

### 1. 资源配额

- 小集群 (<50 nodes): CPU 100m, Memory 128Mi
- 中等集群 (50-200 nodes): CPU 200m, Memory 256Mi
- 大集群 (>200 nodes): CPU 500m, Memory 512Mi

### 2. 检测间隔

- 开发环境: 60 秒
- 生产环境: 300 秒（5分钟）
- 大型集群: 600 秒（10分钟）

### 3. 安全建议

- ✅ 使用 RBAC 最小权限原则
- ✅ Secret 加密存储（使用 K8s Secret Encryption）
- ✅ 启用 Pod Security Policy
- ✅ 定期更新镜像
- ✅ 使用私有镜像仓库

### 4. 日志管理

```bash
# 使用集中式日志系统（如 EFK, Loki）
# 配置日志格式为 JSON
logging:
  format: json
```

### 5. 备份

```bash
# 备份配置
kubectl get configmap opsagent-config -n ops-system -o yaml > backup-config.yaml
kubectl get secret opsagent-secrets -n ops-system -o yaml > backup-secret.yaml
```

## 相关资源

- 📖 [Kubernetes 官方文档](https://kubernetes.io/docs/)
- 📖 [RBAC 权限配置](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- 📖 [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)

## 支持

遇到问题？

1. 查看日志: `./deploy.sh logs`
2. 检查状态: `./deploy.sh status`
3. 查看本文档的故障排查部分
4. 提交 Issue

---

**部署状态**: ✅ 已准备就绪
**版本**: 1.0.0
**最后更新**: 2024年
