# OpsAgent 部署方式总览

本文档概述了 OpsAgent 的所有部署选项，帮助你选择最适合的部署方式。

## 🎯 快速选择

| 场景 | 推荐方式 | 快速开始文档 |
|------|---------|-------------|
| 🏠 **本地开发测试** | Kind + 本地脚本 | [QUICK_START_KIND.md](QUICK_START_KIND.md) |
| 🔄 **本地 CI/CD** | Kind + Self-Hosted Runner | [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md) + [QUICK_START_KIND.md](QUICK_START_KIND.md) |
| 🏢 **内网 K8s 集群** | Self-Hosted Runner | [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md) |
| ☁️ **公网 K8s 集群** | GitHub-Hosted Runner | [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) |
| 🚀 **生产环境** | Self-Hosted Runner | [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) |

## 📊 部署方式对比

### 1. Kind 本地集群 (推荐用于开发)

```
┌─────────────┐    ┌──────────────┐    ┌────────────┐
│  本地代码    │ -> │  Kind 集群    │ -> │  OpsAgent  │
│             │    │  (Docker 内)  │    │  (Pod)     │
└─────────────┘    └──────────────┘    └────────────┘
```

**优点**:
- ✅ 完全本地运行，无需云服务
- ✅ 快速创建和销毁
- ✅ 资源占用少
- ✅ 与真实 K8s 行为一致
- ✅ 免费使用

**缺点**:
- ❌ 仅适合开发测试
- ❌ 单机性能有限

**快速开始**:
```bash
./scripts/deploy-local.sh create
./scripts/deploy-local.sh full
```

**详细文档**: [QUICK_START_KIND.md](QUICK_START_KIND.md) | [KIND_LOCAL_SETUP.md](KIND_LOCAL_SETUP.md)

---

### 2. Kind + Self-Hosted Runner (推荐用于本地 CI/CD)

```
┌─────────┐    ┌──────────────────┐    ┌──────────┐    ┌────────────┐
│ GitHub  │ -> │ Self-Hosted      │ -> │ Kind     │ -> │ OpsAgent   │
│ Push    │    │ Runner (本地)     │    │ 集群     │    │ (Pod)      │
└─────────┘    └──────────────────┘    └──────────┘    └────────────┘
```

**优点**:
- ✅ 自动化 CI/CD
- ✅ 完全本地运行
- ✅ 代码推送自动部署
- ✅ 适合个人开发

**缺点**:
- ❌ 需要本地机器保持运行
- ❌ 仅适合开发测试

**快速开始**:
```bash
# 1. 创建 Kind 集群
./scripts/deploy-local.sh create

# 2. 安装 Self-Hosted Runner (参考文档)

# 3. 推送代码自动部署
git push origin main
```

**详细文档**:
- Runner: [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)
- Kind: [QUICK_START_KIND.md](QUICK_START_KIND.md)
- Workflow: `.github/workflows/deploy-kind.yml`

---

### 3. Self-Hosted Runner + 真实集群 (推荐用于内网生产环境)

```
┌─────────┐    ┌──────────────────┐    ┌──────────────┐    ┌────────────┐
│ GitHub  │ -> │ Self-Hosted      │ -> │ K8s 集群     │ -> │ OpsAgent   │
│ Push    │    │ Runner (内网)     │    │ (生产环境)   │    │ (Pod)      │
└─────────┘    └──────────────────┘    └──────────────┘    └────────────┘
```

**优点**:
- ✅ 可访问内网集群
- ✅ 自动化部署
- ✅ 无限 CI/CD 时间
- ✅ 自定义环境
- ✅ 更快的构建速度

**缺点**:
- ❌ 需要维护 Runner 服务器
- ❌ 有一定安全风险

**快速开始**:
```bash
# 1. 在服务器上安装 Runner
# (参考 QUICK_START_SELF_HOSTED.md)

# 2. 配置 kubeconfig

# 3. 推送代码触发部署
git push origin main
```

**详细文档**:
- [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)
- [SELF_HOSTED_RUNNER_SETUP.md](SELF_HOSTED_RUNNER_SETUP.md)
- Workflow: `.github/workflows/deploy-self-hosted.yml`

---

### 4. GitHub-Hosted Runner (推荐用于公网集群)

```
┌─────────┐    ┌──────────────────┐    ┌──────────────┐    ┌────────────┐
│ GitHub  │ -> │ GitHub-Hosted    │ -> │ K8s 集群     │ -> │ OpsAgent   │
│ Push    │    │ Runner (云端)     │    │ (公网可访问) │    │ (Pod)      │
└─────────┘    └──────────────────┘    └──────────────┘    └────────────┘
```

**优点**:
- ✅ 无需维护基础设施
- ✅ GitHub 官方支持
- ✅ 自动化部署
- ✅ 高可用性

**缺点**:
- ❌ K8s 集群必须公网可访问
- ❌ 有免费时间限制
- ❌ 无法访问内网资源

**快速开始**:
```bash
# 1. 配置 GitHub Secrets (参考文档)
# 2. 推送代码触发部署
git push origin main
```

**详细文档**:
- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- Workflow: `.github/workflows/deploy.yml`

---

### 5. 手动部署 (适合学习和理解)

```
┌─────────┐    ┌──────────┐    ┌──────────────┐    ┌────────────┐
│ 开发者   │ -> │ kubectl  │ -> │ K8s 集群     │ -> │ OpsAgent   │
│         │    │          │    │              │    │ (Pod)      │
└─────────┘    └──────────┘    └──────────────┘    └────────────┘
```

**优点**:
- ✅ 完全可控
- ✅ 便于调试
- ✅ 适合学习

**缺点**:
- ❌ 需要手动操作
- ❌ 容易出错
- ❌ 不适合频繁部署

**快速开始**:
```bash
# 使用部署脚本
cd deploy/k8s
./deploy.sh install

# 或手动部署
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/rbac.yaml
kubectl apply -f deploy/k8s/configmap.yaml
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml
```

**详细文档**: [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)

## 🎓 推荐学习路径

### 初学者

1. **本地 Kind 集群** (1-2 小时)
   - 阅读: [QUICK_START_KIND.md](QUICK_START_KIND.md)
   - 实践: 创建集群并部署应用
   - 目标: 理解 K8s 基本概念

2. **手动部署** (1 小时)
   - 阅读: [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)
   - 实践: 手动部署各个组件
   - 目标: 理解部署流程

### 进阶用户

3. **Self-Hosted Runner** (2-3 小时)
   - 阅读: [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)
   - 实践: 安装 Runner 并配置 CI/CD
   - 目标: 实现自动化部署

4. **Kind + Runner 组合** (1 小时)
   - 实践: 在本地实现完整 CI/CD
   - 目标: 本地开发最佳实践

### 高级用户

5. **生产环境部署** (4-6 小时)
   - 阅读: 所有安全和运维文档
   - 实践: 部署到真实生产环境
   - 目标: 稳定可靠的生产系统

## 📁 文件结构

```
AIOps/
├── .github/workflows/
│   ├── deploy.yml                 # GitHub-Hosted Runner
│   ├── deploy-self-hosted.yml     # Self-Hosted Runner
│   └── deploy-kind.yml            # Kind 集群
├── deploy/k8s/
│   ├── namespace.yaml
│   ├── rbac.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── deploy.sh                  # 手动部署脚本
├── scripts/
│   └── deploy-local.sh            # Kind 本地部署脚本
├── kind-config.yaml               # Kind 集群配置
│
├── QUICK_START_KIND.md            # ⭐ Kind 快速开始
├── QUICK_START_SELF_HOSTED.md    # ⭐ Runner 快速开始
├── GITHUB_ACTIONS_SETUP.md        # GitHub Actions 配置
├── KUBERNETES_DEPLOYMENT.md       # K8s 部署详细指南
├── KIND_LOCAL_SETUP.md            # Kind 详细配置
├── SELF_HOSTED_RUNNER_SETUP.md    # Runner 详细配置
└── DEPLOYMENT_OPTIONS.md          # 本文档
```

## 🎯 常见场景推荐

### 场景 1: "我想在本地快速测试"
**推荐**: Kind 本地集群
```bash
./scripts/deploy-local.sh create
./scripts/deploy-local.sh full
```
**文档**: [QUICK_START_KIND.md](QUICK_START_KIND.md)

---

### 场景 2: "我在开发新功能，需要频繁测试"
**推荐**: Kind + 本地脚本
```bash
# 首次
./scripts/deploy-local.sh full

# 迭代开发
vim src/main.py
./scripts/deploy-local.sh redeploy
./scripts/deploy-local.sh logs
```
**文档**: [QUICK_START_KIND.md](QUICK_START_KIND.md)

---

### 场景 3: "我想实现本地自动化 CI/CD"
**推荐**: Self-Hosted Runner + Kind
```bash
# 1. 创建 Kind 集群
./scripts/deploy-local.sh create

# 2. 安装 Self-Hosted Runner (一次性)

# 3. 开发
git add .
git commit -m "New feature"
git push  # 自动触发部署
```
**文档**: [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md) + [QUICK_START_KIND.md](QUICK_START_KIND.md)

---

### 场景 4: "我的 K8s 集群在内网，无法从公网访问"
**推荐**: Self-Hosted Runner
```bash
# 在能访问内网的服务器上安装 Runner
# 然后推送代码即可自动部署
git push origin main
```
**文档**: [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)

---

### 场景 5: "我的 K8s 集群有公网 API，想用 GitHub Actions"
**推荐**: GitHub-Hosted Runner
```bash
# 配置 Secrets 后，直接推送
git push origin main
```
**文档**: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

---

### 场景 6: "我是 DevOps，要部署到生产环境"
**推荐**: Self-Hosted Runner + 多环境配置
- 阅读所有安全和运维文档
- 使用受限的 ServiceAccount
- 配置监控和告警
- 实施变更管理流程

**文档**: [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)

## 🔒 安全性对比

| 部署方式 | 安全级别 | 注意事项 |
|---------|---------|---------|
| Kind 本地 | 🟢 高 | 仅本地访问 |
| Self-Hosted Runner | 🟡 中 | 仅在私有仓库使用 |
| GitHub-Hosted | 🟢 高 | K8s API 需公网暴露 |
| 手动部署 | 🟢 高 | 取决于操作规范 |

## 💰 成本对比

| 部署方式 | 计算成本 | 维护成本 | 总成本 |
|---------|---------|---------|--------|
| Kind 本地 | 免费 | 低 | 💚 很低 |
| Self-Hosted Runner | 服务器成本 | 中等 | 💛 中等 |
| GitHub-Hosted | 有限免费 | 低 | 💚 低 |
| 手动部署 | K8s 集群成本 | 高 | 💛 中高 |

## 📈 性能对比

| 部署方式 | 构建速度 | 部署速度 | 总耗时 |
|---------|---------|---------|--------|
| Kind 本地 | ⚡⚡⚡ | ⚡⚡⚡ | ~1 分钟 |
| Self-Hosted Runner | ⚡⚡⚡ | ⚡⚡ | ~2 分钟 |
| GitHub-Hosted | ⚡⚡ | ⚡⚡ | ~3-5 分钟 |
| 手动部署 | ⚡⚡ | ⚡ | ~5-10 分钟 |

## 🎁 额外功能对比

| 功能 | Kind | Self-Hosted | GitHub-Hosted | 手动 |
|-----|------|------------|---------------|------|
| 自动化部署 | ❌ | ✅ | ✅ | ❌ |
| PR 预览 | ❌ | ✅ | ✅ | ❌ |
| 多环境支持 | ❌ | ✅ | ✅ | ✅ |
| 回滚功能 | 手动 | ✅ | ✅ | 手动 |
| 健康检查 | 手动 | ✅ | ✅ | 手动 |
| 通知集成 | ❌ | ✅ | ✅ | ❌ |

## 🆘 获取帮助

遇到问题？按优先级查看：

1. **快速开始文档** - 最常见问题的答案
   - [QUICK_START_KIND.md](QUICK_START_KIND.md)
   - [QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md)

2. **详细配置文档** - 深入问题的解答
   - [KIND_LOCAL_SETUP.md](KIND_LOCAL_SETUP.md)
   - [SELF_HOSTED_RUNNER_SETUP.md](SELF_HOSTED_RUNNER_SETUP.md)
   - [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
   - [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)

3. **GitHub Issues** - 提交新问题

## 📝 总结

根据你的需求选择：

- 🏠 **本地开发**: Kind 本地集群 ([QUICK_START_KIND.md](QUICK_START_KIND.md))
- 🔄 **本地 CI/CD**: Self-Hosted Runner + Kind ([QUICK_START_SELF_HOSTED.md](QUICK_START_SELF_HOSTED.md))
- 🏢 **内网生产**: Self-Hosted Runner + 真实集群 ([SELF_HOSTED_RUNNER_SETUP.md](SELF_HOSTED_RUNNER_SETUP.md))
- ☁️ **公网生产**: GitHub-Hosted Runner ([GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md))

**建议学习顺序**: Kind 本地 → Self-Hosted Runner → 生产部署

---

**立即开始**: `./scripts/deploy-local.sh create && ./scripts/deploy-local.sh full` 🚀
