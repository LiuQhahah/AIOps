# OpsAgent K8s 部署文件说明

## 📁 文件清单

### 核心 YAML 文件

| 文件 | 大小 | 用途 | 必需 |
|------|------|------|------|
| `namespace.yaml` | 176B | 创建 ops-system 命名空间 | ✅ |
| `rbac.yaml` | 1.7K | ServiceAccount + ClusterRole + Binding | ✅ |
| `configmap.yaml` | 1.6K | 应用配置文件 | ✅ |
| `deployment.yaml` | 4.5K | OpsAgent Deployment | ✅ |
| `service.yaml` | 939B | ClusterIP Service | ✅ |
| `secret-template.yaml` | 1.6K | Secret 模板（需自行创建） | ⭕ |
| `all-in-one.yaml` | 4.5K | 包含所有资源的单一清单 | ✨ |

### 脚本和工具

| 文件 | 大小 | 用途 |
|------|------|------|
| `deploy.sh` | 7.2K | 自动化部署脚本（可执行） |

### 文档

| 文件 | 大小 | 用途 |
|------|------|------|
| `README.md` | 4.2K | 快速参考指南 |
| `ARCHITECTURE.md` | 25K | 详细架构说明 |
| `FILES_OVERVIEW.md` | 本文件 | 文件说明 |

## 🚀 快速开始

### 最简单的方式

```bash
./deploy.sh install
```

### 使用 all-in-one

```bash
kubectl apply -f all-in-one.yaml
```

### 分步部署

```bash
kubectl apply -f namespace.yaml
kubectl apply -f rbac.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## 📝 文件详解

### namespace.yaml
创建独立的命名空间，隔离 OpsAgent 资源。

### rbac.yaml
包含三个资源：
- **ServiceAccount**: opsagent
- **ClusterRole**: opsagent-reader（只读权限）
- **ClusterRoleBinding**: 绑定二者

### configmap.yaml
应用配置，包括：
- Kubernetes 配置（in_cluster: true）
- 检测间隔（300秒）
- 日志级别（INFO）
- Metrics 配置

### deployment.yaml
OpsAgent 部署配置，包括：
- 镜像：opsagent:latest
- 资源限制：CPU 200m-1000m, Memory 256Mi-512Mi
- 健康检查：liveness + readiness probes
- 安全配置：非 root 用户运行
- 卷挂载：ConfigMap

### service.yaml
ClusterIP 服务，暴露两个端口：
- 80 → 18080 (API)
- 9090 (Metrics)

包含 ServiceMonitor（如果使用 Prometheus Operator）

### secret-template.yaml
Secret 模板，用于存储：
- AWS 凭证（可选）
- Azure 凭证（可选）
- GitHub Token（可选）
- 通知配置（可选）

需要手动创建或使用 kubectl create secret

### all-in-one.yaml
包含除 Secret 外的所有资源，方便一键部署。

## 🛠️ deploy.sh 命令

```bash
./deploy.sh install      # 安装
./deploy.sh uninstall    # 卸载
./deploy.sh upgrade      # 升级
./deploy.sh status       # 查看状态
./deploy.sh logs         # 实时日志
./deploy.sh shell        # 进入 Pod
./deploy.sh port-forward # 端口转发
./deploy.sh build        # 构建镜像
```

## 📖 推荐阅读顺序

1. **README.md** - 快速了解基本用法
2. **本文件** - 理解各文件作用
3. **ARCHITECTURE.md** - 深入了解架构
4. **YAML 文件** - 查看具体配置

## 🔗 相关文档

- [../../KUBERNETES_DEPLOYMENT.md](../../KUBERNETES_DEPLOYMENT.md) - 完整部署指南
- [../../K8S_DEPLOYMENT_CHECKLIST.md](../../K8S_DEPLOYMENT_CHECKLIST.md) - 部署检查清单
- [../../K8S_DEPLOYMENT_SUMMARY.md](../../K8S_DEPLOYMENT_SUMMARY.md) - 部署总结

---
