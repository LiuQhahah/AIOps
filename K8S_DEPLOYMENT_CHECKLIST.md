# OpsAgent K8s 部署检查清单

在将 OpsAgent 部署到 Kubernetes 集群之前，请完成以下检查清单。

## ✅ 部署前检查

### 环境准备

- [ ] Kubernetes 集群版本 >= 1.19
- [ ] kubectl 已安装并配置正确
- [ ] 有集群管理员权限（创建 ClusterRole）
- [ ] Docker 已安装（用于构建镜像）

### 资源检查

```bash
# 检查集群连接
kubectl cluster-info

# 检查节点状态
kubectl get nodes

# 检查可用资源
kubectl top nodes  # 需要 metrics-server
```

### 镜像准备

- [ ] 已构建 Docker 镜像
  ```bash
  docker build -t opsagent:latest .
  ```

- [ ] (可选) 镜像已推送到仓库
  ```bash
  docker tag opsagent:latest your-registry/opsagent:latest
  docker push your-registry/opsagent:latest
  ```

- [ ] 已修改 deployment.yaml 中的镜像地址

### 配置准备

- [ ] 已检查 `configmap.yaml` 中的配置
  - [ ] `k8s.in_cluster: true`
  - [ ] `detection.interval` 设置合理
  - [ ] `remediation.enabled: false` (首次部署建议)
  - [ ] `logging.level` 合适（建议 INFO）

- [ ] (可选) 如需使用 AWS/Azure，已创建 Secret
  ```bash
  kubectl create secret generic opsagent-secrets \
    --from-literal=aws-access-key-id=YOUR_KEY \
    --namespace=ops-system
  ```

## 🚀 部署步骤

### 方式 1: 自动化部署（推荐）

```bash
cd deploy/k8s
./deploy.sh install
```

- [ ] 命令执行成功
- [ ] 无错误输出

### 方式 2: 一键部署清单

```bash
kubectl apply -f deploy/k8s/all-in-one.yaml
```

- [ ] 所有资源创建成功

### 方式 3: 分步部署

```bash
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/rbac.yaml
kubectl apply -f deploy/k8s/configmap.yaml
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml
```

- [ ] Namespace 创建成功
- [ ] RBAC 配置成功
- [ ] ConfigMap 创建成功
- [ ] Deployment 创建成功
- [ ] Service 创建成功

## ✅ 部署后验证

### 1. 检查资源状态

```bash
# 检查 Namespace
kubectl get ns ops-system

# 检查 ServiceAccount
kubectl get sa opsagent -n ops-system

# 检查 ClusterRole 和 Binding
kubectl get clusterrole opsagent-reader
kubectl get clusterrolebinding opsagent-reader-binding

# 检查 ConfigMap
kubectl get cm opsagent-config -n ops-system

# 检查 Deployment
kubectl get deployment opsagent -n ops-system
```

- [ ] 所有资源都存在
- [ ] 无错误状态

### 2. 检查 Pod 状态

```bash
kubectl get pods -n ops-system
```

期望输出：
```
NAME                        READY   STATUS    RESTARTS   AGE
opsagent-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

- [ ] Pod 状态为 `Running`
- [ ] `READY` 显示 `1/1`
- [ ] `RESTARTS` 为 `0` 或很小的数字

如果 Pod 未就绪：
```bash
# 查看详细信息
kubectl describe pod -l app=opsagent -n ops-system

# 查看事件
kubectl get events -n ops-system --sort-by='.lastTimestamp'
```

### 3. 检查日志

```bash
kubectl logs -f deployment/opsagent -n ops-system
```

期望看到的日志：
```
INFO Starting OpsAgent...
INFO Loaded in-cluster Kubernetes configuration
INFO K8s detectors initialized
INFO Detection scheduler started
INFO Detection cycle started
INFO Running Pod resource detection
INFO Detection cycle completed total_issues=X
```

- [ ] 日志中有 "Starting OpsAgent"
- [ ] 日志中有 "K8s detectors initialized"
- [ ] 日志中有 "Detection scheduler started"
- [ ] 无 ERROR 级别日志（WARNING 可以接受）

### 4. 测试健康检查

```bash
kubectl exec deployment/opsagent -n ops-system -- curl -s localhost:18080/health
```

期望输出：
```json
{"status": "healthy"}
```

- [ ] 健康检查返回成功

### 5. 测试 Metrics

```bash
# 端口转发
kubectl port-forward -n ops-system svc/opsagent 9090:9090 &

# 测试 metrics 端点
curl -s http://localhost:9090/metrics | grep opsagent

# 停止端口转发
kill %1
```

- [ ] Metrics 端点可访问
- [ ] 能看到 opsagent 相关指标

### 6. 验证检测功能

等待至少一个检测周期（默认 5 分钟），然后检查日志：

```bash
kubectl logs deployment/opsagent -n ops-system | grep "Detection cycle completed"
```

期望看到：
```
INFO Detection cycle completed total_issues=X
```

- [ ] 检测周期已运行
- [ ] 日志中显示发现的问题数量

### 7. 验证 RBAC 权限

```bash
# 测试能否列出 Deployments
kubectl auth can-i list deployments \
  --as=system:serviceaccount:ops-system:opsagent

# 测试能否删除 Deployments（应该返回 no）
kubectl auth can-i delete deployments \
  --as=system:serviceaccount:ops-system:opsagent
```

- [ ] 可以列出资源（返回 `yes`）
- [ ] 不能删除资源（返回 `no`）

### 8. 检查 Service

```bash
kubectl get svc opsagent -n ops-system
```

- [ ] Service 存在
- [ ] Type 为 `ClusterIP`
- [ ] Endpoints 不为空

```bash
kubectl get endpoints opsagent -n ops-system
```

## ⚠️ 常见问题

### Pod 一直处于 Pending

```bash
kubectl describe pod -l app=opsagent -n ops-system
```

检查：
- [ ] 节点资源是否充足
- [ ] 是否有节点选择器或污点配置

### Pod CrashLoopBackOff

```bash
kubectl logs deployment/opsagent -n ops-system --previous
```

检查：
- [ ] 镜像是否正确
- [ ] ConfigMap 配置是否正确
- [ ] 是否有权限问题

### ImagePullBackOff

检查：
- [ ] 镜像名称是否正确
- [ ] 镜像仓库是否可访问
- [ ] 是否需要配置 imagePullSecrets

### 权限错误

```bash
kubectl logs deployment/opsagent -n ops-system | grep Forbidden
```

检查：
- [ ] ServiceAccount 是否正确绑定
- [ ] ClusterRole 权限是否配置
- [ ] ClusterRoleBinding 是否正确

## 🎯 性能基准

部署成功后，监控以下指标：

- [ ] **CPU 使用率**: 应低于 500m
- [ ] **内存使用率**: 应低于 256Mi
- [ ] **检测周期耗时**: 应低于 30 秒（取决于集群大小）
- [ ] **Pod 重启次数**: 应为 0

监控命令：
```bash
# 查看资源使用
kubectl top pod -n ops-system

# 持续监控
watch kubectl top pod -n ops-system
```

## 📊 访问应用

### 本地访问（端口转发）

```bash
# API 端口
kubectl port-forward -n ops-system deployment/opsagent 18080:18080

# 访问
curl http://localhost:18080/health

# Metrics 端口
kubectl port-forward -n ops-system deployment/opsagent 9090:9090
curl http://localhost:9090/metrics
```

### 集群内访问

```
http://opsagent.ops-system.svc.cluster.local
http://opsagent.ops-system.svc.cluster.local:9090/metrics
```

## 🔒 安全检查

- [ ] Pod 以非 root 用户运行
- [ ] RBAC 权限遵循最小权限原则（只读）
- [ ] Secret 正确配置（如果使用）
- [ ] 敏感信息未硬编码在 ConfigMap 中

## 📝 下一步

部署验证完成后：

1. [ ] 观察几个检测周期，确认正常运行
2. [ ] 根据实际情况调整检测间隔
3. [ ] (可选) 配置 Grafana Dashboard 监控指标
4. [ ] (可选) 配置告警规则
5. [ ] 规划下一阶段功能（如启用自动修复）

## 📖 相关文档

- 完整部署文档: [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)
- 快速参考: [deploy/k8s/README.md](deploy/k8s/README.md)
- 检测器文档: [K8S_DETECTOR_QUICK_START.md](K8S_DETECTOR_QUICK_START.md)

## ✅ 部署完成

所有检查项都通过后，OpsAgent 已成功部署到 Kubernetes 集群！

```bash
# 查看最终状态
cd deploy/k8s
./deploy.sh status
```

---

**检查清单版本**: 1.0.0
**适用于**: OpsAgent v1.0.0
**最后更新**: 2024年
