# OpsAgent K8s 部署 - 快速参考

## 🚀 一键部署

```bash
# 进入部署目录
cd deploy/k8s

# 安装（自动构建镜像并部署）
./deploy.sh install

# 查看状态
./deploy.sh status
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `namespace.yaml` | 创建 ops-system 命名空间 |
| `rbac.yaml` | RBAC 权限配置 (ServiceAccount, ClusterRole) |
| `configmap.yaml` | 应用配置文件 |
| `secret-template.yaml` | Secret 模板（需自行创建 secret.yaml） |
| `deployment.yaml` | OpsAgent Deployment |
| `service.yaml` | ClusterIP Service 和 ServiceMonitor |
| `deploy.sh` | 一键部署脚本 |

## 🛠️ 常用命令

### 部署管理

```bash
./deploy.sh install      # 安装
./deploy.sh uninstall    # 卸载
./deploy.sh upgrade      # 升级
./deploy.sh status       # 查看状态
```

### 日志和调试

```bash
./deploy.sh logs         # 查看实时日志
./deploy.sh shell        # 进入 Pod Shell
./deploy.sh port-forward # 端口转发到本地
```

### 构建镜像

```bash
./deploy.sh build        # 只构建镜像
```

## ⚙️ 配置修改

### 修改检测间隔

编辑 `configmap.yaml`:

```yaml
detection:
  interval: 300  # 秒
```

然后重启：

```bash
kubectl apply -f configmap.yaml
kubectl rollout restart deployment/opsagent -n ops-system
```

### 添加云服务凭证

```bash
kubectl create secret generic opsagent-secrets \
  --from-literal=aws-access-key-id=YOUR_KEY \
  --from-literal=aws-secret-access-key=YOUR_SECRET \
  --namespace=ops-system
```

### 修改镜像

编辑 `deployment.yaml`:

```yaml
image: your-registry/opsagent:v1.0.0
```

## 🔍 验证部署

```bash
# 1. 检查 Pod
kubectl get pods -n ops-system

# 2. 查看日志
kubectl logs -f deployment/opsagent -n ops-system

# 3. 测试健康检查
kubectl exec deployment/opsagent -n ops-system -- curl localhost:18080/health

# 4. 访问 API（端口转发）
kubectl port-forward -n ops-system deployment/opsagent 18080:18080
curl http://localhost:18080/health
```

## 🐛 故障排查

### Pod 启动失败

```bash
# 查看事件
kubectl describe pod -l app=opsagent -n ops-system

# 查看日志
kubectl logs deployment/opsagent -n ops-system
```

### 权限错误

```bash
# 检查 ServiceAccount
kubectl get sa opsagent -n ops-system

# 检查 ClusterRole
kubectl describe clusterrole opsagent-reader

# 检查绑定
kubectl get clusterrolebinding opsagent-reader-binding
```

### 配置问题

```bash
# 查看 ConfigMap
kubectl get cm opsagent-config -n ops-system -o yaml

# 进入 Pod 检查
kubectl exec -it deployment/opsagent -n ops-system -- /bin/bash
cat /app/config/config.yaml
```

## 📊 监控

### Prometheus Metrics

```bash
# 端口转发
kubectl port-forward -n ops-system svc/opsagent 9090:9090

# 访问
curl http://localhost:9090/metrics
```

### 关键指标

- `opsagent_detection_runs_total` - 检测运行次数
- `opsagent_issues_found_total` - 发现的问题数量
- `opsagent_detection_duration_seconds` - 检测耗时

## 🔐 RBAC 权限

OpsAgent 拥有以下权限（只读）：

- ✅ 读取 Deployments, StatefulSets, DaemonSets
- ✅ 读取 Pods, Services, ConfigMaps
- ✅ 读取 Namespaces, Nodes
- ✅ 读取 Metrics（可选）
- ❌ 无写入权限（安全）

## 📝 最佳实践

1. **首次部署**: 设置 `remediation.enabled: false`，只检测不修复
2. **资源配额**: 根据集群大小调整 CPU/Memory
3. **检测间隔**: 生产环境建议 300 秒（5分钟）
4. **单实例运行**: 避免重复检测
5. **日志格式**: 生产环境使用 JSON 格式

## 🔗 相关文档

- 📖 完整部署指南: [KUBERNETES_DEPLOYMENT.md](../../KUBERNETES_DEPLOYMENT.md)
- 📖 应用配置: [config.yaml](configmap.yaml)
- 📖 项目文档: [README.md](../../README.md)

## 📞 快速帮助

```bash
# 查看帮助
./deploy.sh help

# 示例输出:
# install       安装 OpsAgent
# uninstall     卸载 OpsAgent
# upgrade       升级 OpsAgent
# status        查看 OpsAgent 状态
# logs          查看实时日志
# shell         进入 Pod Shell
# port-forward  端口转发
# build         构建 Docker 镜像
```

---

**提示**: 首次部署前，请确保已阅读 [完整部署指南](../../KUBERNETES_DEPLOYMENT.md)
