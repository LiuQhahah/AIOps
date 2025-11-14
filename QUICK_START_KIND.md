# Kind 本地部署 - 3 分钟快速开始 🚀

在本地 kind 集群中运行 OpsAgent，最简单的方式！

## ⚡ 超快速开始（3 步搞定）

```bash
# 1️⃣ 安装 kind (如果还没有)
brew install kind  # macOS
# 或 Linux: curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64 && chmod +x kind && sudo mv kind /usr/local/bin/

# 2️⃣ 创建集群
./scripts/deploy-local.sh create

# 3️⃣ 部署应用
./scripts/deploy-local.sh full
```

就这么简单！✨

## 📍 访问应用

```bash
# 端口转发
./scripts/deploy-local.sh port-forward

# 在另一个终端访问
curl http://localhost:18080/health

# 或在浏览器打开
open http://localhost:18080
```

## 🔄 开发工作流

```bash
# 修改代码后快速重部署
./scripts/deploy-local.sh redeploy

# 查看日志
./scripts/deploy-local.sh logs

# 查看状态
./scripts/deploy-local.sh status
```

## 🛠️ 常用命令

```bash
./scripts/deploy-local.sh create        # 创建集群
./scripts/deploy-local.sh full          # 完整部署
./scripts/deploy-local.sh redeploy      # 快速重部署（开发用）
./scripts/deploy-local.sh status        # 查看状态
./scripts/deploy-local.sh logs          # 查看日志
./scripts/deploy-local.sh port-forward  # 端口转发
./scripts/deploy-local.sh health        # 健康检查
./scripts/deploy-local.sh cleanup       # 清理资源
./scripts/deploy-local.sh delete        # 删除集群
./scripts/deploy-local.sh help          # 查看帮助
```

## 🎯 典型开发流程

```bash
# 1. 首次设置
./scripts/deploy-local.sh create
./scripts/deploy-local.sh full

# 2. 开发循环
vim src/detectors/pod_resource_detector.py  # 修改代码
./scripts/deploy-local.sh redeploy          # 重新部署
./scripts/deploy-local.sh logs              # 查看日志

# 3. 测试
./scripts/deploy-local.sh health            # 健康检查
curl http://localhost:18080/api/issues      # 测试 API

# 4. 清理
./scripts/deploy-local.sh cleanup           # 清理资源
./scripts/deploy-local.sh delete            # 删除集群
```

## 🔧 手动步骤（如果你喜欢手动控制）

```bash
# 1. 创建集群
kind create cluster --config kind-config.yaml --name opsagent-dev

# 2. 构建镜像
docker build -t opsagent:latest .

# 3. 加载到 kind
kind load docker-image opsagent:latest --name opsagent-dev

# 4. 部署
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/rbac.yaml
kubectl apply -f deploy/k8s/configmap.yaml
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml

# 5. 等待就绪
kubectl rollout status deployment/opsagent -n ops-system

# 6. 访问
kubectl port-forward -n ops-system svc/opsagent 18080:80
```

## ⚙️ 配置

### 修改应用配置

编辑 `deploy/k8s/configmap.yaml`，然后：

```bash
kubectl apply -f deploy/k8s/configmap.yaml
kubectl rollout restart deployment/opsagent -n ops-system
```

### 修改资源配额

编辑 `deploy/k8s/deployment.yaml` 中的 resources 部分：

```yaml
resources:
  requests:
    cpu: 100m      # 修改为你需要的值
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

## 🐛 故障排查

### Pod 无法启动

```bash
# 查看 Pod 状态
kubectl get pods -n ops-system

# 查看详细信息
kubectl describe pod -n ops-system -l app=opsagent

# 查看日志
kubectl logs -n ops-system -l app=opsagent
```

### 镜像拉取失败

```bash
# 确保镜像已构建
docker images | grep opsagent

# 重新加载镜像
kind load docker-image opsagent:latest --name opsagent-dev

# 检查 imagePullPolicy (应该是 Never 或 IfNotPresent)
kubectl get deployment opsagent -n ops-system -o yaml | grep imagePullPolicy
```

### 无法访问应用

```bash
# 确认 Service 存在
kubectl get svc -n ops-system

# 确认 Pod 运行
kubectl get pods -n ops-system

# 测试内部连接
kubectl exec -n ops-system deployment/opsagent -- curl http://localhost:18080/health

# 使用端口转发
kubectl port-forward -n ops-system svc/opsagent 18080:80
```

## 💡 使用技巧

### 1. 快速命令别名

添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
alias kops='kubectl -n ops-system'
alias klogs='kubectl logs -f -n ops-system -l app=opsagent'
alias kredeploy='./scripts/deploy-local.sh redeploy'
alias kpf='kubectl port-forward -n ops-system svc/opsagent 18080:80'
```

使用：

```bash
kops get pods        # 查看 pods
klogs                # 查看日志
kredeploy            # 快速重部署
kpf                  # 端口转发
```

### 2. 保存集群状态

```bash
# 导出配置
kubectl get all -n ops-system -o yaml > cluster-state.yaml

# 备份镜像
docker save opsagent:latest -o opsagent-backup.tar

# 恢复
kind load image-archive opsagent-backup.tar --name opsagent-dev
kubectl apply -f cluster-state.yaml
```

### 3. 多版本测试

```bash
# 构建不同版本
docker build -t opsagent:v1 .
docker build -t opsagent:v2 .

# 加载到 kind
kind load docker-image opsagent:v1 --name opsagent-dev
kind load docker-image opsagent:v2 --name opsagent-dev

# 切换版本
kubectl set image deployment/opsagent opsagent=opsagent:v2 -n ops-system
```

## 🎓 进阶用法

### 使用 Self-Hosted Runner + Kind

1. **安装 Self-Hosted Runner**（参考 QUICK_START_SELF_HOSTED.md）
2. **创建 Kind 集群**（一次性）
3. **推送代码自动部署**

```bash
# 设置完成后，只需：
git add .
git commit -m "Update feature"
git push origin main

# GitHub Actions 会自动：
# - 构建镜像
# - 加载到 kind
# - 部署更新
# - 运行测试
```

### 集成到 IDE

**VS Code**: 安装 Kubernetes 扩展

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Deploy to Kind",
      "type": "shell",
      "command": "./scripts/deploy-local.sh redeploy",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

按 `Cmd+Shift+B` 即可部署！

## 📚 更多文档

- 详细指南: [KIND_LOCAL_SETUP.md](KIND_LOCAL_SETUP.md)
- Self-Hosted Runner: [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)
- K8s 部署: [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)

## ❓ 常见问题

**Q: Kind 和 Docker Desktop K8s 有什么区别？**
A: Kind 更轻量、启动更快、支持多节点，更适合 CI/CD。

**Q: 需要多少资源？**
A: 最低 2 CPU + 4GB 内存，推荐 4 CPU + 8GB 内存。

**Q: 可以在 Kind 中运行多个应用吗？**
A: 可以！就像正常的 K8s 集群一样。

**Q: 如何持久化数据？**
A: 使用 PersistentVolume，或在 kind-config.yaml 中配置 hostPath。

**Q: 删除集群会丢失数据吗？**
A: 是的，建议在删除前备份重要数据。

---

**开始使用**: `./scripts/deploy-local.sh create && ./scripts/deploy-local.sh full` 🚀

**遇到问题？** 查看 [KIND_LOCAL_SETUP.md](KIND_LOCAL_SETUP.md) 详细文档
