# GitHub Actions 自动部署配置指南

本文档说明如何配置 GitHub Actions 来自动构建 Docker 镜像并部署到 Kubernetes 集群。

## 📋 目录

- [工作流程说明](#工作流程说明)
- [前置要求](#前置要求)
- [配置步骤](#配置步骤)
- [使用方法](#使用方法)
- [故障排查](#故障排查)

## 工作流程说明

GitHub Actions workflow (`.github/workflows/deploy.yml`) 包含三个主要任务：

### 1. Build and Push (构建并推送镜像)
- 从代码构建 Docker 镜像
- 自动生成镜像标签（基于分支和 commit SHA）
- 推送镜像到 Docker Hub
- 使用 GitHub Actions 缓存加速构建

### 2. Deploy (部署到 Kubernetes)
- 配置 kubectl 连接到集群
- 创建/更新 Kubernetes 资源
- 等待部署完成
- 验证部署状态

### 3. Notify (通知部署结果)
- 显示部署成功或失败信息
- 可扩展为发送通知到 Slack/Teams 等

## 前置要求

### 1. Docker Hub 账号
- 注册 [Docker Hub](https://hub.docker.com/) 账号
- 获取用户名和密码（或 Access Token）

### 2. Kubernetes 集群
- 有一个可访问的 Kubernetes 集群
- 集群版本 v1.19+
- 有集群管理员权限

### 3. GitHub 仓库
- 将代码推送到 GitHub 仓库
- 有仓库的 Settings 权限（用于配置 Secrets）

## 配置步骤

### 步骤 1: 配置 Docker Hub Secrets

在你的 GitHub 仓库中配置 Secrets：

1. 进入仓库的 `Settings` → `Secrets and variables` → `Actions`

2. 点击 `New repository secret` 添加以下 secrets：

#### 必需的 Secrets:

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `DOCKER_USERNAME` | Docker Hub 用户名 | 你的 Docker Hub 账号 |
| `DOCKER_PASSWORD` | Docker Hub 密码或 Token | 密码或 [创建 Access Token](https://hub.docker.com/settings/security) |
| `KUBECONFIG` | Kubernetes 配置文件（Base64 编码） | 见下方说明 |

### 步骤 2: 获取并配置 KUBECONFIG

#### 方法 1: 从本地 kubeconfig 文件

```bash
# 1. 确认你的 kubeconfig 可以正常连接集群
kubectl cluster-info

# 2. Base64 编码 kubeconfig 文件
cat ~/.kube/config | base64 | tr -d '\n'

# 3. 复制输出的 base64 字符串，添加到 GitHub Secrets 中的 KUBECONFIG
```

#### 方法 2: 创建专用的 ServiceAccount（推荐用于生产环境）

```bash
# 1. 创建 ServiceAccount
kubectl create serviceaccount github-actions -n ops-system

# 2. 创建 ClusterRoleBinding (赋予集群管理员权限)
kubectl create clusterrolebinding github-actions-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=ops-system:github-actions

# 3. 获取 ServiceAccount Token
TOKEN=$(kubectl -n ops-system create token github-actions --duration=87600h)

# 4. 获取集群信息
CLUSTER_NAME=$(kubectl config view --minify -o jsonpath='{.clusters[0].name}')
CLUSTER_SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
CLUSTER_CA=$(kubectl config view --minify --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')

# 5. 生成 kubeconfig 文件
cat <<EOF > github-actions-kubeconfig.yaml
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: ${CLUSTER_CA}
    server: ${CLUSTER_SERVER}
  name: ${CLUSTER_NAME}
contexts:
- context:
    cluster: ${CLUSTER_NAME}
    user: github-actions
  name: github-actions
current-context: github-actions
users:
- name: github-actions
  user:
    token: ${TOKEN}
EOF

# 6. Base64 编码
cat github-actions-kubeconfig.yaml | base64 | tr -d '\n'

# 7. 复制输出，添加到 GitHub Secrets
# 8. 删除临时文件
rm github-actions-kubeconfig.yaml
```

### 步骤 3: 配置可选的 Secrets（如果应用需要）

如果你的 OpsAgent 需要访问云服务或发送通知，配置以下可选 secrets：

| Secret 名称 | 用途 | 是否必需 |
|------------|------|---------|
| `AWS_ACCESS_KEY_ID` | AWS 访问密钥 | 可选 |
| `AWS_SECRET_ACCESS_KEY` | AWS 密钥 | 可选 |
| `GH_TOKEN` | GitHub Personal Access Token | 可选 |
| `TEAMS_WEBHOOK_URL` | Microsoft Teams Webhook URL | 可选 |

### 步骤 4: 验证配置

配置完成后，检查所有必需的 Secrets 是否已添加：

```
Settings → Secrets and variables → Actions → Repository secrets

必需:
✓ DOCKER_USERNAME
✓ DOCKER_PASSWORD
✓ KUBECONFIG

可选:
○ AWS_ACCESS_KEY_ID
○ AWS_SECRET_ACCESS_KEY
○ GH_TOKEN
```

## 使用方法

### 自动触发部署

当你推送代码到 `main` 分支时，GitHub Actions 会自动触发：

```bash
# 提交并推送代码
git add .
git commit -m "Update application"
git push origin main

# GitHub Actions 将自动:
# 1. 构建 Docker 镜像
# 2. 推送到 Docker Hub
# 3. 部署到 Kubernetes 集群
```

### 手动触发部署

1. 进入 GitHub 仓库的 `Actions` 标签页
2. 选择 `Build and Deploy to Kubernetes` workflow
3. 点击 `Run workflow` 按钮
4. 选择分支并点击绿色的 `Run workflow` 按钮

### 查看部署状态

1. 在 `Actions` 标签页查看工作流运行状态
2. 点击具体的运行实例查看详细日志
3. 每个步骤都有详细的执行日志

### 镜像标签策略

GitHub Actions 会自动为镜像创建多个标签：

| 触发条件 | 生成的标签 | 示例 |
|---------|-----------|------|
| Push to main | `main-{commit-sha}` | `main-abc1234` |
| Push to main | `latest` | `latest` |
| Push to branch | `{branch-name}` | `develop` |
| Create tag v1.0.0 | `v1.0.0`, `1.0`, `1` | `v1.0.0` |

## 验证部署

### 在 GitHub Actions 中验证

工作流完成后，会在日志中显示：

```
=== Deployment Status ===
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
opsagent   1/1     1            1           2m

=== Pods Status ===
NAME                        READY   STATUS    RESTARTS   AGE
opsagent-xxxxx-xxxxx        1/1     Running   0          2m

=== Recent Logs ===
INFO Starting OpsAgent...
INFO Detection scheduler started
```

### 在本地验证

```bash
# 检查 deployment 状态
kubectl get deployment opsagent -n ops-system

# 检查 pod 状态
kubectl get pods -n ops-system

# 查看日志
kubectl logs -f deployment/opsagent -n ops-system

# 检查使用的镜像版本
kubectl get deployment opsagent -n ops-system -o jsonpath='{.spec.template.spec.containers[0].image}'
```

## 故障排查

### 常见问题

#### 1. Docker Hub 推送失败

**错误**: `denied: requested access to the resource is denied`

**解决方案**:
- 检查 `DOCKER_USERNAME` 和 `DOCKER_PASSWORD` 是否正确
- 确认 Docker Hub 账号已验证邮箱
- 考虑使用 Access Token 代替密码

#### 2. Kubernetes 连接失败

**错误**: `The connection to the server localhost:8080 was refused`

**解决方案**:
```bash
# 重新检查 KUBECONFIG secret
echo $KUBECONFIG_BASE64 | base64 -d | kubectl --kubeconfig=- cluster-info

# 确保 kubeconfig 中的服务器地址可以从 GitHub Actions 访问
# (不能是 localhost 或内网 IP)
```

#### 3. 权限不足

**错误**: `Error from server (Forbidden): deployments.apps is forbidden`

**解决方案**:
- 确保 ServiceAccount 有足够权限
- 检查 ClusterRoleBinding 配置
- 考虑使用 cluster-admin 角色（仅用于测试）

#### 4. 镜像拉取失败

**错误**: `ImagePullBackOff` 或 `ErrImagePull`

**解决方案**:
```bash
# 确认镜像已成功推送到 Docker Hub
docker pull your-username/opsagent:latest

# 如果是私有仓库,需要创建 imagePullSecret
kubectl create secret docker-registry regcred \
  --docker-server=docker.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  -n ops-system

# 然后在 deployment.yaml 中添加:
# spec:
#   template:
#     spec:
#       imagePullSecrets:
#         - name: regcred
```

#### 5. 部署超时

**错误**: `error: timed out waiting for the condition`

**解决方案**:
```bash
# 检查 pod 事件
kubectl describe pod -l app=opsagent -n ops-system

# 查看详细日志
kubectl logs deployment/opsagent -n ops-system --previous

# 检查资源是否充足
kubectl describe node
```

### 调试技巧

#### 查看完整的 GitHub Actions 日志

1. 点击失败的 workflow run
2. 展开每个步骤查看详细输出
3. 特别关注红色的错误信息

#### 本地测试 kubeconfig

```bash
# 解码 GitHub Secret 中的 KUBECONFIG
echo "YOUR_BASE64_KUBECONFIG" | base64 -d > test-kubeconfig.yaml

# 测试连接
kubectl --kubeconfig=test-kubeconfig.yaml cluster-info
kubectl --kubeconfig=test-kubeconfig.yaml get nodes

# 删除测试文件
rm test-kubeconfig.yaml
```

#### 测试 Docker 构建

```bash
# 本地构建镜像
docker build -t opsagent:test .

# 测试运行
docker run --rm opsagent:test

# 推送到 Docker Hub 测试
docker tag opsagent:test your-username/opsagent:test
docker push your-username/opsagent:test
```

## 高级配置

### 多环境部署

如果需要部署到多个环境（开发、测试、生产），可以：

1. 创建多个 workflow 文件：
   - `.github/workflows/deploy-dev.yml`
   - `.github/workflows/deploy-staging.yml`
   - `.github/workflows/deploy-prod.yml`

2. 使用不同的触发条件和 secrets

3. 或使用 GitHub Environments 功能

### 添加通知

在 workflow 的 `notify` job 中添加通知步骤：

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment to Kubernetes'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 回滚部署

如果需要回滚到之前的版本：

```bash
# 查看部署历史
kubectl rollout history deployment/opsagent -n ops-system

# 回滚到上一个版本
kubectl rollout undo deployment/opsagent -n ops-system

# 回滚到特定版本
kubectl rollout undo deployment/opsagent -n ops-system --to-revision=2
```

## 安全最佳实践

1. **使用 Access Token 而不是密码**
   - Docker Hub: 创建 Access Token
   - GitHub: 使用 Personal Access Token

2. **限制 ServiceAccount 权限**
   - 不要使用 cluster-admin（除非必要）
   - 创建自定义 Role 和 RoleBinding

3. **定期轮换 Secrets**
   - 定期更新 KUBECONFIG token
   - 更新 Docker Hub credentials

4. **使用 Environment Secrets**
   - 为不同环境使用不同的 secrets
   - 启用 Required reviewers

5. **启用审计日志**
   - 记录所有部署操作
   - 监控异常访问

## 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Hub 文档](https://docs.docker.com/docker-hub/)
- [kubectl 文档](https://kubernetes.io/docs/reference/kubectl/)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

## 支持

遇到问题？

1. 查看 GitHub Actions 运行日志
2. 阅读本文档的故障排查部分
3. 检查 Kubernetes 集群日志
4. 提交 Issue 并附上错误信息

---

**文档版本**: 1.0.0
**最后更新**: 2024年
**状态**: ✅ 已验证
