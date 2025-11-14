# CI/CD 和部署文档总览

本文档汇总了所有 CI/CD 和 Kubernetes 部署相关的文件和文档。

## 🚀 快速开始（选择一个）

| 如果你想... | 那么使用... | 时间 |
|-----------|-----------|------|
| 💻 在本地快速测试 | [QUICK_START_KIND.md](QUICK_START_KIND.md) | 3 分钟 |
| 🔄 本地自动化 CI/CD | [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md) | 5 分钟 |
| ☁️ 部署到云端 K8s | [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) | 10 分钟 |
| 📚 了解所有选项 | [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md) | 5 分钟 |

## 📁 文件清单

### ⭐ 快速开始文档（推荐从这里开始）

| 文件 | 说明 | 适用场景 |
|-----|------|---------|
| [QUICK_START_KIND.md](QUICK_START_KIND.md) | Kind 本地部署 3 分钟快速开始 | 🏠 本地开发测试 |
| [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md) | Self-Hosted Runner 5 分钟快速开始 | 🔄 本地/内网 CI/CD |
| [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md) | 所有部署方式对比和选择指南 | 🎯 选择部署方案 |

### 📖 详细配置文档

| 文件 | 说明 | 何时阅读 |
|-----|------|---------|
| [KIND_LOCAL_SETUP.md](KIND_LOCAL_SETUP.md) | Kind 完整安装配置指南 | 需要深入了解 Kind |
| [SELF_HOSTED_RUNNER_SETUP.md](SELF_HOSTED_RUNNER_SETUP.md) | Runner 完整安装和安全配置 | 生产环境部署 Runner |
| [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) | GitHub Actions 完整配置指南 | 使用 GitHub-hosted runner |
| [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) | K8s 部署完整指南（62 页） | 理解 K8s 部署细节 |
| [K8S_DEPLOYMENT_CHECKLIST.md](K8S_DEPLOYMENT_CHECKLIST.md) | K8s 部署检查清单 | 部署前验证 |
| [K8S_DEPLOYMENT_SUMMARY.md](K8S_DEPLOYMENT_SUMMARY.md) | K8s 部署总结 | 快速参考 |

### ⚙️ 配置文件

| 文件 | 说明 | 用途 |
|-----|------|-----|
| `kind-config.yaml` | Kind 集群配置 | 创建本地 Kind 集群 |
| `.github/workflows/deploy.yml` | GitHub-Hosted Runner workflow | 云端 CI/CD |
| `.github/workflows/deploy-self-hosted.yml` | Self-Hosted Runner workflow | 内网 CI/CD |
| `.github/workflows/deploy-kind.yml` | Kind 专用 workflow | 本地 Kind CI/CD |
| `.github/workflows/README.md` | Workflows 说明 | 了解 workflows |

### 🛠️ 脚本工具

| 文件 | 说明 | 使用场景 |
|-----|------|---------|
| `scripts/deploy-local.sh` | Kind 本地部署一键脚本 | 本地开发快速部署 |
| `deploy/k8s/deploy.sh` | K8s 手动部署脚本 | 手动部署到任意 K8s |

### 📦 K8s 清单文件

所有文件位于 `deploy/k8s/` 目录：

| 文件 | 资源类型 | 说明 |
|-----|---------|-----|
| `namespace.yaml` | Namespace | ops-system 命名空间 |
| `rbac.yaml` | RBAC | ServiceAccount + ClusterRole |
| `configmap.yaml` | ConfigMap | 应用配置 |
| `deployment.yaml` | Deployment | OpsAgent 部署 |
| `service.yaml` | Service | ClusterIP Service |
| `secret-template.yaml` | Secret | Secret 模板（需填写） |
| `all-in-one.yaml` | All | 一键部署清单 |

## 🎯 使用指南

### 场景 1: 本地开发 (推荐新手)

```bash
# 1. 阅读快速开始
cat QUICK_START_KIND.md

# 2. 创建 Kind 集群
./scripts/deploy-local.sh create

# 3. 部署应用
./scripts/deploy-local.sh full

# 4. 开发迭代
vim src/main.py
./scripts/deploy-local.sh redeploy
```

**相关文档**:
- [QUICK_START_KIND.md](QUICK_START_KIND.md) - 快速开始
- [KIND_LOCAL_SETUP.md](KIND_LOCAL_SETUP.md) - 详细配置
- `scripts/deploy-local.sh` - 部署脚本

---

### 场景 2: 本地 CI/CD

```bash
# 1. 创建 Kind 集群
./scripts/deploy-local.sh create

# 2. 安装 Self-Hosted Runner
# 参考 QUICK_START_SELF_HOSTED.md

# 3. 推送代码自动部署
git add .
git commit -m "New feature"
git push origin main
```

**相关文档**:
- [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md) - Runner 快速开始
- [QUICK_START_KIND.md](QUICK_START_KIND.md) - Kind 配置
- `.github/workflows/deploy-kind.yml` - Workflow 文件

---

### 场景 3: 内网 K8s 生产环境

```bash
# 1. 在能访问 K8s 的服务器上安装 Runner
# 参考 QUICK_START_SELF_HOSTED.md

# 2. 配置 kubeconfig

# 3. 推送代码部署
git push origin main
```

**相关文档**:
- [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md) - 快速开始
- [SELF_HOSTED_RUNNER_SETUP.md](SELF_HOSTED_RUNNER_SETUP.md) - 详细配置
- [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) - K8s 部署
- `.github/workflows/deploy-self-hosted.yml` - Workflow 文件

---

### 场景 4: 公网 K8s (AWS EKS, 阿里云 ACK 等)

```bash
# 1. 配置 GitHub Secrets
# 参考 GITHUB_ACTIONS_SETUP.md

# 2. 推送代码部署
git push origin main
```

**相关文档**:
- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - 完整配置
- [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) - K8s 部署
- `.github/workflows/deploy.yml` - Workflow 文件

---

### 场景 5: 手动部署（学习用）

```bash
# 使用部署脚本
cd deploy/k8s
./deploy.sh install

# 或手动逐步部署
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/rbac.yaml
kubectl apply -f deploy/k8s/configmap.yaml
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml
```

**相关文档**:
- [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) - 详细部署指南
- [K8S_DEPLOYMENT_CHECKLIST.md](K8S_DEPLOYMENT_CHECKLIST.md) - 检查清单

## 📚 推荐阅读顺序

### 🌟 初学者路径

1. **选择部署方式** (5 分钟)
   - 阅读: [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)
   - 决定使用哪种部署方式

2. **本地快速体验** (10 分钟)
   - 阅读: [QUICK_START_KIND.md](QUICK_START_KIND.md)
   - 实践: 在本地 Kind 集群部署应用

3. **理解 K8s 部署** (30 分钟)
   - 阅读: [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) 的前半部分
   - 理解部署架构和资源配置

### 🚀 进阶用户路径

4. **配置 CI/CD** (30 分钟)
   - 阅读: [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)
   - 实践: 安装 Self-Hosted Runner

5. **本地自动化** (20 分钟)
   - 组合使用 Kind + Self-Hosted Runner
   - 实现本地完整 CI/CD 流程

### 🎓 高级用户路径

6. **生产环境配置** (2 小时)
   - 阅读: [SELF_HOSTED_RUNNER_SETUP.md](SELF_HOSTED_RUNNER_SETUP.md)
   - 阅读: [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) 安全部分
   - 配置监控、告警、备份

7. **多环境部署** (1 小时)
   - 配置 dev/staging/prod 环境
   - 实施变更管理流程

## 🔍 文档查找指南

**我想知道...**

- ❓ **如何选择部署方式** → [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)
- ❓ **如何在本地快速测试** → [QUICK_START_KIND.md](QUICK_START_KIND.md)
- ❓ **如何配置 CI/CD** → [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)
- ❓ **Kind 详细配置** → [KIND_LOCAL_SETUP.md](KIND_LOCAL_SETUP.md)
- ❓ **Runner 详细配置** → [SELF_HOSTED_RUNNER_SETUP.md](SELF_HOSTED_RUNNER_SETUP.md)
- ❓ **K8s 部署细节** → [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)
- ❓ **GitHub Actions 配置** → [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- ❓ **部署检查清单** → [K8S_DEPLOYMENT_CHECKLIST.md](K8S_DEPLOYMENT_CHECKLIST.md)
- ❓ **故障排查** → 各详细文档的"故障排查"章节

## 🎯 快速命令参考

### Kind 本地部署

```bash
./scripts/deploy-local.sh create        # 创建集群
./scripts/deploy-local.sh full          # 完整部署
./scripts/deploy-local.sh redeploy      # 快速重部署
./scripts/deploy-local.sh status        # 查看状态
./scripts/deploy-local.sh logs          # 查看日志
./scripts/deploy-local.sh port-forward  # 端口转发
./scripts/deploy-local.sh help          # 帮助信息
```

### K8s 手动部署

```bash
cd deploy/k8s
./deploy.sh install     # 安装
./deploy.sh status      # 状态
./deploy.sh logs        # 日志
./deploy.sh uninstall   # 卸载
```

### kubectl 常用命令

```bash
kubectl get pods -n ops-system                          # 查看 pods
kubectl logs -f -n ops-system -l app=opsagent          # 查看日志
kubectl describe deployment opsagent -n ops-system     # 查看详情
kubectl port-forward -n ops-system svc/opsagent 18080:80  # 端口转发
```

## 📊 文档统计

- **快速开始文档**: 3 个 (⭐ 推荐阅读)
- **详细配置文档**: 6 个
- **Workflow 文件**: 3 个
- **部署脚本**: 2 个
- **K8s 清单**: 7 个
- **配置文件**: 1 个

**总文档页数**: 约 150+ 页
**总覆盖场景**: 5+ 种部署方式

## 🎁 额外资源

### 官方文档链接

- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Kind 官方文档](https://kind.sigs.k8s.io/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker 文档](https://docs.docker.com/)

### 相关工具

- [kubectl](https://kubernetes.io/docs/tasks/tools/) - K8s 命令行工具
- [k9s](https://k9scli.io/) - K8s TUI 管理工具
- [Lens](https://k8slens.dev/) - K8s IDE
- [Helm](https://helm.sh/) - K8s 包管理器

## 🆘 获取帮助

1. **查看相关快速开始文档** - 大部分问题都有答案
2. **查看详细配置文档的故障排查章节**
3. **查看 GitHub Workflow 运行日志**
4. **在 GitHub 提交 Issue**

## ✅ 下一步建议

根据你的情况选择：

### 如果你是新手
1. ✅ 阅读 [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)
2. ✅ 跟随 [QUICK_START_KIND.md](QUICK_START_KIND.md) 实践
3. ✅ 理解 [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) 架构部分

### 如果你想本地开发
1. ✅ 按照 [QUICK_START_KIND.md](QUICK_START_KIND.md) 设置环境
2. ✅ 使用 `./scripts/deploy-local.sh` 快速迭代
3. ✅ (可选) 配置 Self-Hosted Runner 实现自动化

### 如果你要部署生产环境
1. ✅ 完整阅读 [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)
2. ✅ 配置 [SELF_HOSTED_RUNNER_SETUP.md](SELF_HOSTED_RUNNER_SETUP.md)
3. ✅ 使用 [K8S_DEPLOYMENT_CHECKLIST.md](K8S_DEPLOYMENT_CHECKLIST.md) 验证
4. ✅ 实施监控和告警

---

**开始使用**:

- 🏠 本地开发: `./scripts/deploy-local.sh create && ./scripts/deploy-local.sh full`
- 🔄 CI/CD: 查看 [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)
- 📚 了解更多: 阅读 [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)

**Have fun! 🚀**
