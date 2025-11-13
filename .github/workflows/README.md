# GitHub Actions Workflows

这个目录包含 GitHub Actions 自动化工作流配置文件。

## 工作流列表

### deploy.yml - 构建并部署到 Kubernetes

**触发条件**:
- 推送到 `main` 分支
- 手动触发 (workflow_dispatch)

**功能**:
1. 构建 Docker 镜像并推送到 Docker Hub
2. 部署到 Kubernetes 集群
3. 验证部署状态
4. 发送部署通知

**所需 Secrets**:
- `DOCKER_USERNAME` - Docker Hub 用户名
- `DOCKER_PASSWORD` - Docker Hub 密码或 Access Token
- `KUBECONFIG` - Kubernetes 配置文件 (Base64 编码)

**可选 Secrets** (应用功能需要):
- `AWS_ACCESS_KEY_ID` - AWS 访问密钥
- `AWS_SECRET_ACCESS_KEY` - AWS 密钥
- `GH_TOKEN` - GitHub Personal Access Token

## 快速开始

详细配置说明请参考: [GITHUB_ACTIONS_SETUP.md](../../GITHUB_ACTIONS_SETUP.md)

### 基本步骤

1. **配置 Docker Hub Secrets**
   ```
   Settings → Secrets → Actions → New repository secret
   - DOCKER_USERNAME: 你的 Docker Hub 用户名
   - DOCKER_PASSWORD: 你的 Docker Hub 密码/Token
   ```

2. **配置 KUBECONFIG Secret**
   ```bash
   # Base64 编码你的 kubeconfig
   cat ~/.kube/config | base64 | tr -d '\n'

   # 添加到 GitHub Secrets (名称: KUBECONFIG)
   ```

3. **推送代码触发部署**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

4. **查看部署状态**
   - 访问 GitHub 仓库的 Actions 标签页
   - 查看工作流运行状态和日志

## 工作流架构

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Actions Runner                   │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Job 1: Build and Push                             │ │
│  │  - Checkout code                                   │ │
│  │  - Build Docker image                              │ │
│  │  - Push to Docker Hub                              │ │
│  │  - Generate image tags                             │ │
│  └────────────────────────────────────────────────────┘ │
│                          ↓                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Job 2: Deploy                                     │ │
│  │  - Setup kubectl                                   │ │
│  │  - Connect to K8s cluster                          │ │
│  │  - Deploy RBAC, ConfigMap, Deployment, Service    │ │
│  │  - Wait for rollout                                │ │
│  │  - Verify deployment                               │ │
│  └────────────────────────────────────────────────────┘ │
│                          ↓                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Job 3: Notify                                     │ │
│  │  - Send deployment result notification             │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 镜像标签策略

| 触发事件 | 生成的标签 |
|---------|-----------|
| Push to main | `main-{commit-sha}`, `latest` |
| Push to branch | `{branch-name}` |
| Create tag v1.0.0 | `v1.0.0`, `1.0`, `1` |

## 故障排查

### 常见错误

1. **镜像推送失败**: 检查 Docker Hub credentials
2. **K8s 连接失败**: 验证 KUBECONFIG secret
3. **部署超时**: 检查集群资源和 pod 状态
4. **权限错误**: 确保 ServiceAccount 有足够权限

详细故障排查指南: [GITHUB_ACTIONS_SETUP.md#故障排查](../../GITHUB_ACTIONS_SETUP.md#故障排查)

## 相关文档

- [完整配置指南](../../GITHUB_ACTIONS_SETUP.md)
- [Kubernetes 部署文档](../../KUBERNETES_DEPLOYMENT.md)
- [部署检查清单](../../K8S_DEPLOYMENT_CHECKLIST.md)

---

**维护**: 定期检查并更新工作流配置
**安全**: 定期轮换 Secrets
**监控**: 关注工作流运行状态和失败通知
