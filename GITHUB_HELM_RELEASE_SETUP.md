# GitHub Actions 自动发布 Helm Chart 设置指南

针对仓库：https://github.com/LiuQhahah/AIOps

## 🎯 功能说明

每次代码合并到 `main` 分支时，自动：
1. ✅ 生成新的版本号
2. ✅ 打包 Helm Chart
3. ✅ 推送到 GitHub Container Registry (GHCR)
4. ✅ 构建并推送 Docker 镜像
5. ✅ 生成安装说明

## 🚀 快速设置（5 分钟）

### 步骤 1: 确认权限（已自动配置）

workflow 文件中已经配置了所需权限：
```yaml
permissions:
  contents: write
  packages: write
  id-token: write
```

这些权限使用 `GITHUB_TOKEN`，**无需额外配置**。

### 步骤 2: 推送 workflow 文件

```bash
cd /Users/qiang_liu/Downloads/workspace/AIOps

# 添加 workflow 文件
git add .github/workflows/release-helm.yml

# 提交
git commit -m "Add automated Helm Chart release workflow"

# 推送到 GitHub
git push origin main
```

### 步骤 3: 触发首次发布

推送任何代码到 main 分支即可触发：

```bash
# 方式 1: 直接推送到 main
git add .
git commit -m "Update helm chart"
git push origin main

# 方式 2: 通过 PR 合并到 main
# 创建 PR → Review → Merge

# 方式 3: 手动触发
# GitHub → Actions → Release Helm Chart → Run workflow
```

### 步骤 4: 查看发布结果

1. **查看 Actions 运行状态**
   - 访问: https://github.com/LiuQhahah/AIOps/actions
   - 点击最新的 "Release Helm Chart" workflow

2. **查看发布的 Helm Chart**
   - 访问: https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent
   - 或: https://github.com/users/LiuQhahah/packages

3. **查看发布的 Docker 镜像**
   - 访问: https://github.com/LiuQhahah/AIOps/pkgs/container/aiops

## 📦 使用发布的 Helm Chart

### 基本安装

```bash
# 安装最新版本
helm install opsagent oci://ghcr.io/liuqhahah/opsagent \
  --namespace ops-system \
  --create-namespace

# 安装指定版本
helm install opsagent oci://ghcr.io/liuqhahah/opsagent --version 1.0.0 \
  --namespace ops-system \
  --create-namespace
```

### 查看可用版本

```bash
# 方式 1: 通过 GitHub Packages 页面
# https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent

# 方式 2: 使用 Helm 命令（需要先 pull）
helm show chart oci://ghcr.io/liuqhahah/opsagent
```

### 升级到新版本

```bash
helm upgrade opsagent oci://ghcr.io/liuqhahah/opsagent \
  --namespace ops-system
```

## 🔧 Workflow 工作原理

### 版本号生成规则

```
Chart.yaml 中的 version: 1.0.0
↓
在 main 分支: 使用原始版本 → 1.0.0
在其他分支: 添加构建号 → 1.0.0-123
↓
appVersion: 使用 git commit SHA → abc1234
```

### 触发条件

workflow 会在以下情况触发：
1. ✅ Push 到 main 分支
2. ✅ 修改了以下文件：
   - `helm/**` (Helm Chart 文件)
   - `src/**` (源代码)
   - `Dockerfile`
   - workflow 文件本身
3. ✅ 手动触发 (workflow_dispatch)

### 执行流程

```
1. 检出代码
   ↓
2. 安装 Helm
   ↓
3. 生成版本号
   ↓
4. 更新 Chart.yaml 版本
   ↓
5. Lint 检查 Chart
   ↓
6. 打包 Chart
   ↓
7. 推送到 GHCR
   ↓
8. 构建 Docker 镜像（并行）
   ↓
9. 推送 Docker 镜像
   ↓
10. 生成安装说明
```

## 🎨 自定义配置

### 修改版本号规则

编辑 `.github/workflows/release-helm.yml`，找到 "Generate version number" 步骤：

```yaml
- name: Generate version number
  id: version
  run: |
    CHART_VERSION=$(grep '^version:' helm/opsagent/Chart.yaml | awk '{print $2}')
    SHORT_SHA=$(git rev-parse --short HEAD)

    # 自定义版本号规则
    # 示例 1: 使用日期 + SHA
    # VERSION="${CHART_VERSION}-$(date +%Y%m%d)-${SHORT_SHA}"

    # 示例 2: 使用构建号
    BUILD_NUMBER=$(git rev-list --count HEAD)
    VERSION="${CHART_VERSION}-${BUILD_NUMBER}"

    echo "version=$VERSION" >> $GITHUB_OUTPUT
```

### 仅在特定条件下触发

```yaml
# 只在特定文件变更时触发
on:
  push:
    branches:
      - main
    paths:
      - 'helm/**'        # 只有 helm 目录变化才触发
      - 'Dockerfile'     # 或 Dockerfile 变化
```

### 添加通知

在 workflow 末尾添加通知步骤：

```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Helm Chart ${{ steps.version.outputs.version }} released!"
      }
```

### 添加测试步骤

在 "Package Helm Chart" 之前添加：

```yaml
- name: Test Helm Chart
  run: |
    # 创建测试 values
    cat > test-values.yaml <<EOF
    replicaCount: 1
    image:
      pullPolicy: Never
    EOF

    # 测试模板渲染
    helm template opsagent helm/opsagent --values test-values.yaml > /dev/null

    # 使用 helm unittest（如果有）
    # helm unittest helm/opsagent
```

## 📊 监控和调试

### 查看 Actions 日志

1. 访问: https://github.com/LiuQhahah/AIOps/actions
2. 点击具体的 workflow 运行
3. 展开步骤查看详细日志

### 常见问题

#### 问题 1: 权限错误

```
Error: failed to authorize: failed to fetch oauth token: unexpected status: 401
```

**原因**: GITHUB_TOKEN 权限不足

**解决**:
workflow 文件中已配置权限：
```yaml
permissions:
  contents: write
  packages: write
```

确保仓库设置中允许 Actions 写入：
- Settings → Actions → General → Workflow permissions → Read and write permissions

#### 问题 2: Chart 推送失败

```
Error: failed to push: chart already exists
```

**原因**: Chart 版本号已存在

**解决**:
- 更新 `helm/opsagent/Chart.yaml` 中的 version
- 或让自动版本号生成处理

#### 问题 3: 找不到发布的 Chart

**解决**:
1. 检查 Packages 页面: https://github.com/LiuQhahah?tab=packages
2. 如果 Package 是私有的，需要配置访问权限
3. 设置为公开：Package settings → Change visibility → Public

### 手动测试 workflow

```bash
# 在本地测试打包
cd /Users/qiang_liu/Downloads/workspace/AIOps
helm lint helm/opsagent
helm package helm/opsagent

# 模拟推送（需要先登录）
echo $GITHUB_TOKEN | helm registry login ghcr.io -u LiuQhahah --password-stdin
helm push opsagent-1.0.0.tgz oci://ghcr.io/liuqhahah
```

## 🔐 安全配置

### 设置 Package 可见性

发布后，默认 Package 是私有的。设置为公开：

1. 访问: https://github.com/users/LiuQhahah/packages/container/opsagent/settings
2. Danger Zone → Change visibility → Public
3. 确认操作

### 配置 Package 权限

如果需要团队访问：
1. Package settings → Manage Actions access
2. Add repository
3. 选择需要访问的仓库

## 📈 版本管理最佳实践

### 语义化版本

在 `helm/opsagent/Chart.yaml` 中遵循 [SemVer](https://semver.org/)：

```yaml
version: 1.0.0  # MAJOR.MINOR.PATCH

# MAJOR: 不兼容的变更
# MINOR: 向后兼容的新功能
# PATCH: 向后兼容的 bug 修复
```

### 发布流程建议

```bash
# 1. 开发新功能（在 feature 分支）
git checkout -b feature/new-detector
# ... 开发 ...
git commit -am "Add new detector"

# 2. 更新版本号（如果是 minor 版本）
# 编辑 helm/opsagent/Chart.yaml
# version: 1.0.0 → 1.1.0

# 3. 创建 PR
git push origin feature/new-detector
# 在 GitHub 创建 PR

# 4. Review 和 Merge
# PR 合并到 main 后，自动触发 Helm Chart 发布

# 5. 验证发布
# 访问 Actions 页面确认发布成功
```

### 使用 Git Tags（可选）

如果想为重要版本创建 tag：

```bash
# 创建标签
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# workflow 会在 tag 推送时创建 GitHub Release
```

## 🎯 完整工作流示例

### 场景：发布新版本

```bash
# 1. 确认当前在 main 分支
git checkout main
git pull origin main

# 2. 创建新功能分支
git checkout -b feature/add-azure-detector

# 3. 开发新功能
# ... 编写代码 ...

# 4. 提交代码
git add .
git commit -m "feat: add Azure resource detector"

# 5. 推送分支
git push origin feature/add-azure-detector

# 6. 在 GitHub 创建 Pull Request

# 7. Code Review 后合并到 main

# 8. 自动触发：
#    - Helm Chart 打包
#    - 推送到 GHCR
#    - Docker 镜像构建
#    - 生成安装说明

# 9. 查看发布结果
#    https://github.com/LiuQhahah/AIOps/actions
#    https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent

# 10. 使用新版本
helm upgrade opsagent oci://ghcr.io/liuqhahah/opsagent
```

## 🔗 相关链接

- **仓库**: https://github.com/LiuQhahah/AIOps
- **Actions**: https://github.com/LiuQhahah/AIOps/actions
- **Packages**: https://github.com/LiuQhahah?tab=packages
- **Helm 文档**: [HELM_DEPLOYMENT.md](HELM_DEPLOYMENT.md)
- **快速开始**: [HELM_QUICK_START.md](HELM_QUICK_START.md)

## ✅ 检查清单

部署前确认：

- [ ] workflow 文件已推送到 `.github/workflows/release-helm.yml`
- [ ] 仓库设置允许 Actions 写入 (Settings → Actions)
- [ ] `helm/opsagent/Chart.yaml` 版本号正确
- [ ] 已测试本地打包: `helm lint helm/opsagent`
- [ ] 已推送到 GitHub 并触发 Actions
- [ ] Actions 运行成功
- [ ] Package 可见性设置正确（公开/私有）
- [ ] 可以正常安装: `helm install opsagent oci://ghcr.io/liuqhahah/opsagent`

---

**准备好了吗？** 推送代码到 main 分支，开始自动发布！🚀

```bash
git add .
git commit -m "Setup automated Helm Chart release"
git push origin main
```

然后访问: https://github.com/LiuQhahah/AIOps/actions 查看执行情况！
