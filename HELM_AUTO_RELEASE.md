# Helm Chart 自动发布 - 快速参考

针对仓库：https://github.com/LiuQhahah/AIOps

## ⚡ 超快速设置（3 步）

### 1️⃣ 推送 Workflow 文件

```bash
cd /Users/qiang_liu/Downloads/workspace/AIOps

git add .github/workflows/release-helm.yml
git commit -m "Add automated Helm release workflow"
git push origin main
```

### 2️⃣ 等待 Actions 完成

访问查看进度：
```
https://github.com/LiuQhahah/AIOps/actions
```

### 3️⃣ 使用发布的 Chart

```bash
helm install opsagent oci://ghcr.io/liuqhahah/opsagent \
  --namespace ops-system \
  --create-namespace
```

就这么简单！✨

---

## 🎯 工作原理

```
代码推送到 main
    ↓
GitHub Actions 触发
    ↓
自动生成版本号（基于 Chart.yaml + build number）
    ↓
打包 Helm Chart
    ↓
推送到 GitHub Container Registry
    ↓
构建 Docker 镜像（并行）
    ↓
完成！可以直接使用
```

---

## 📦 发布的内容

每次 merge 到 main 后，自动发布：

1. **Helm Chart**
   - 位置: `ghcr.io/liuqhahah/opsagent`
   - 查看: https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent

2. **Docker 镜像**
   - 位置: `ghcr.io/liuqhahah/aiops`
   - 标签: `latest`, `main-{sha}`, `{branch}`

---

## 🔄 版本号规则

### Main 分支
```
Chart.yaml version: 1.0.0
→ 发布版本: 1.0.0
→ appVersion: {commit-sha}
```

### 其他分支
```
Chart.yaml version: 1.0.0
→ 发布版本: 1.0.0-{build-number}
→ appVersion: {commit-sha}
```

---

## 📋 常用命令

### 安装最新版本
```bash
helm install opsagent oci://ghcr.io/liuqhahah/opsagent
```

### 安装指定版本
```bash
helm install opsagent oci://ghcr.io/liuqhahah/opsagent --version 1.0.0
```

### 升级到最新版本
```bash
helm upgrade opsagent oci://ghcr.io/liuqhahah/opsagent
```

### 查看发布的版本
```
访问: https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent
```

### 查看 Chart 信息
```bash
helm show chart oci://ghcr.io/liuqhahah/opsagent
helm show values oci://ghcr.io/liuqhahah/opsagent
```

---

## 🔧 发布新版本

### 方式 1: 直接推送（快速修复）
```bash
# 修改代码
git add .
git commit -m "fix: bug fix"
git push origin main
# 自动触发发布
```

### 方式 2: 通过 PR（推荐）
```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发和提交
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 3. 创建 PR 并合并到 main
# 合并后自动触发发布
```

### 方式 3: 手动触发
```
GitHub → Actions → Release Helm Chart → Run workflow
```

---

## 🎨 修改版本号

### 小版本更新（Bug 修复）
```bash
# 编辑 helm/opsagent/Chart.yaml
version: 1.0.0 → 1.0.1

# 提交并推送
git add helm/opsagent/Chart.yaml
git commit -m "chore: bump version to 1.0.1"
git push origin main
```

### 功能更新
```bash
version: 1.0.0 → 1.1.0
```

### 重大更新
```bash
version: 1.0.0 → 2.0.0
```

---

## 🔍 监控发布

### 查看 Actions 状态
```
https://github.com/LiuQhahah/AIOps/actions
```

### 查看发布的 Packages
```
https://github.com/LiuQhahah?tab=packages
```

### 查看最新发布
```
https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent
```

---

## ⚠️ 故障排查

### 问题 1: Actions 失败

```bash
# 查看 Actions 日志
访问: https://github.com/LiuQhahah/AIOps/actions

# 常见原因:
# - Helm Chart 语法错误 → 运行 helm lint
# - 权限不足 → 检查 Settings → Actions → Workflow permissions
```

### 问题 1.5: invalid_reference: invalid repository

**错误信息**:
```
Error: invalid_reference: invalid repository
```

**原因**: GitHub Container Registry (GHCR) 要求 repository 名称必须**全部小写**。如果你的 GitHub 用户名包含大写字母（如 `LiuQhahah`），直接使用会导致错误。

**解决方案**: workflow 文件已经修复，使用 `tr` 命令将用户名转换为小写：
```bash
REPO_OWNER=$(echo "${{ github.repository_owner }}" | tr '[:upper:]' '[:lower:]')
helm push $CHART_FILE oci://ghcr.io/${REPO_OWNER}
```

**正确的 URL 格式**:
- ❌ 错误: `oci://ghcr.io/LiuQhahah/opsagent`
- ✅ 正确: `oci://ghcr.io/liuqhahah/opsagent`

**验证方法**:
```bash
# 安装时使用小写
helm install opsagent oci://ghcr.io/liuqhahah/opsagent
```

### 问题 2: 找不到发布的 Chart

```bash
# 检查 Package 是否为私有
访问: https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent/settings

# 设置为公开:
Change visibility → Public
```

### 问题 3: 安装失败

```bash
# 确认版本号
helm show chart oci://ghcr.io/liuqhahah/opsagent

# 尝试不指定版本
helm install opsagent oci://ghcr.io/liuqhahah/opsagent

# 查看详细错误
helm install opsagent oci://ghcr.io/liuqhahah/opsagent --debug
```

---

## 🎯 完整示例

### 发布新功能完整流程

```bash
# 1. 创建功能分支
git checkout -b feature/add-detector
git push -u origin feature/add-detector

# 2. 开发功能
vim src/detectors/new_detector.py
git add .
git commit -m "feat: add new detector"

# 3. 更新版本号（如果需要）
vim helm/opsagent/Chart.yaml
# version: 1.0.0 → 1.1.0
git add helm/opsagent/Chart.yaml
git commit -m "chore: bump version to 1.1.0"

# 4. 推送并创建 PR
git push origin feature/add-detector
# 在 GitHub 创建 Pull Request

# 5. Review 后合并到 main
# Merge PR

# 6. 自动触发发布
# 查看: https://github.com/LiuQhahah/AIOps/actions

# 7. 等待发布完成（约 3-5 分钟）

# 8. 验证发布
helm show chart oci://ghcr.io/liuqhahah/opsagent

# 9. 部署新版本
helm upgrade opsagent oci://ghcr.io/liuqhahah/opsagent --version 1.1.0
```

---

## 📊 发布统计

查看所有发布历史：
```
https://github.com/LiuQhahah/AIOps/actions?query=workflow%3A%22Release+Helm+Chart%22
```

查看所有版本：
```
https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent/versions
```

---

## 📚 相关文档

- **详细设置指南**: [GITHUB_HELM_RELEASE_SETUP.md](GITHUB_HELM_RELEASE_SETUP.md)
- **Helm 仓库说明**: [HELM_REPOSITORY.md](HELM_REPOSITORY.md)
- **Helm 部署指南**: [HELM_DEPLOYMENT.md](HELM_DEPLOYMENT.md)
- **快速开始**: [HELM_QUICK_START.md](HELM_QUICK_START.md)

---

## ✅ 快速检查清单

推送前确认：

- [ ] Workflow 文件在 `.github/workflows/release-helm.yml`
- [ ] `helm/opsagent/Chart.yaml` 版本号正确
- [ ] 本地测试通过: `helm lint helm/opsagent`
- [ ] 代码已提交到 main 分支

推送后确认：

- [ ] Actions 运行成功
- [ ] Package 已发布
- [ ] 可以正常安装

---

**现在就开始！** 🚀

```bash
git add .github/workflows/release-helm.yml
git commit -m "Add automated Helm release"
git push origin main
```

然后访问: https://github.com/LiuQhahah/AIOps/actions
