# Helm Chart 仓库配置指南

关于 Helm Chart 的存储、分发和使用。

## 📦 Helm Chart 存储方式

### 1. 本地文件系统（当前方式）

```bash
# 我们创建的 Chart 在本地
./helm/opsagent/

# 使用本地 Chart 安装
helm install opsagent ./helm/opsagent
```

**优点**:
- ✅ 开发时快速迭代
- ✅ 完全可控
- ✅ 无需网络

**缺点**:
- ❌ 不便于分享
- ❌ 团队协作困难
- ❌ 需要访问源代码

---

### 2. Helm Chart 仓库（HTTP/HTTPS）

这是最常用的远程存储方式。

#### 公共 Helm 仓库

```bash
# Bitnami 仓库（最大的公共 Helm 仓库之一）
helm repo add bitnami https://charts.bitnami.com/bitnami

# Prometheus 社区仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Nginx Ingress 仓库
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

# 更新仓库索引
helm repo update

# 从远程仓库安装
helm install my-nginx bitnami/nginx
```

#### 搭建私有 Helm 仓库的方式

##### 方式 1: GitHub Pages（免费、推荐用于开源项目）

```bash
# 1. 在 GitHub 创建仓库（如 helm-charts）

# 2. 在本地打包 Chart
helm package ./helm/opsagent
# 生成: opsagent-1.0.0.tgz

# 3. 创建 index.yaml
helm repo index . --url https://your-username.github.io/helm-charts/

# 4. 推送到 GitHub
git add .
git commit -m "Add opsagent chart"
git push origin main

# 5. 启用 GitHub Pages
# Settings → Pages → Source: main branch → /root

# 6. 使用远程 Chart
helm repo add my-charts https://your-username.github.io/helm-charts/
helm repo update
helm install opsagent my-charts/opsagent
```

##### 方式 2: Harbor（企业级，推荐用于生产）

```bash
# Harbor 是一个企业级 Docker Registry，也支持 Helm Chart

# 1. 部署 Harbor
# 参考: https://goharbor.io/docs/

# 2. 在 Harbor 中创建项目（如 opsagent）

# 3. 推送 Chart
helm package ./helm/opsagent
helm push opsagent-1.0.0.tgz oci://harbor.example.com/opsagent

# 4. 使用 Chart
helm install opsagent oci://harbor.example.com/opsagent/opsagent --version 1.0.0
```

##### 方式 3: ChartMuseum（轻量级）

```bash
# 1. 部署 ChartMuseum
docker run -d \
  -p 8080:8080 \
  -e DEBUG=1 \
  -e STORAGE=local \
  -e STORAGE_LOCAL_ROOTDIR=/charts \
  -v $(pwd)/charts:/charts \
  chartmuseum/chartmuseum:latest

# 2. 推送 Chart
curl --data-binary "@opsagent-1.0.0.tgz" http://localhost:8080/api/charts

# 3. 添加仓库
helm repo add my-repo http://localhost:8080
helm repo update

# 4. 安装
helm install opsagent my-repo/opsagent
```

##### 方式 4: AWS S3 + CloudFront

```bash
# 1. 创建 S3 bucket
aws s3 mb s3://my-helm-charts

# 2. 打包并上传
helm package ./helm/opsagent
aws s3 cp opsagent-1.0.0.tgz s3://my-helm-charts/

# 3. 生成 index
helm repo index . --url https://my-helm-charts.s3.amazonaws.com/
aws s3 cp index.yaml s3://my-helm-charts/

# 4. 配置 CloudFront（可选，加速访问）

# 5. 使用
helm repo add my-charts https://my-helm-charts.s3.amazonaws.com/
helm install opsagent my-charts/opsagent
```

##### 方式 5: 阿里云 OSS

```bash
# 1. 创建 OSS Bucket

# 2. 打包并上传
helm package ./helm/opsagent
ossutil cp opsagent-1.0.0.tgz oss://my-helm-charts/

# 3. 生成 index
helm repo index . --url https://my-helm-charts.oss-cn-beijing.aliyuncs.com/
ossutil cp index.yaml oss://my-helm-charts/

# 4. 使用
helm repo add my-charts https://my-helm-charts.oss-cn-beijing.aliyuncs.com/
helm install opsagent my-charts/opsagent
```

---

### 3. OCI 注册表（推荐，现代化方式）

Helm 3.8+ 支持将 Chart 存储在 OCI（Open Container Initiative）注册表中。

#### Docker Hub

```bash
# 1. 登录 Docker Hub
echo $DOCKER_PASSWORD | helm registry login -u $DOCKER_USERNAME --password-stdin registry-1.docker.io

# 2. 打包 Chart
helm package ./helm/opsagent

# 3. 推送到 Docker Hub
helm push opsagent-1.0.0.tgz oci://registry-1.docker.io/your-username

# 4. 安装
helm install opsagent oci://registry-1.docker.io/your-username/opsagent --version 1.0.0
```

#### GitHub Container Registry (ghcr.io)

```bash
# 1. 创建 GitHub Personal Access Token
# Settings → Developer settings → Personal access tokens
# 权限: write:packages, read:packages

# 2. 登录
echo $GITHUB_TOKEN | helm registry login ghcr.io -u your-username --password-stdin

# 3. 推送
helm package ./helm/opsagent
helm push opsagent-1.0.0.tgz oci://ghcr.io/your-username

# 4. 安装
helm install opsagent oci://ghcr.io/your-username/opsagent --version 1.0.0
```

#### AWS ECR

```bash
# 1. 登录 ECR
aws ecr get-login-password --region us-east-1 | \
  helm registry login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# 2. 创建 ECR 仓库
aws ecr create-repository --repository-name opsagent

# 3. 推送
helm package ./helm/opsagent
helm push opsagent-1.0.0.tgz oci://123456789012.dkr.ecr.us-east-1.amazonaws.com

# 4. 安装
helm install opsagent \
  oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/opsagent \
  --version 1.0.0
```

#### 阿里云 ACR

```bash
# 1. 登录 ACR
helm registry login --username=your-username registry.cn-hangzhou.aliyuncs.com

# 2. 推送
helm package ./helm/opsagent
helm push opsagent-1.0.0.tgz oci://registry.cn-hangzhou.aliyuncs.com/your-namespace

# 3. 安装
helm install opsagent \
  oci://registry.cn-hangzhou.aliyuncs.com/your-namespace/opsagent \
  --version 1.0.0
```

---

### 4. Git 仓库

直接从 Git 仓库安装（不推荐用于生产，但适合开发）。

```bash
# 使用 Helm 插件
helm plugin install https://github.com/aslafy-z/helm-git

# 从 Git 仓库安装
helm install opsagent git+https://github.com/your-org/opsagent@helm/opsagent?ref=main
```

---

## 🎯 推荐方案对比

| 方案 | 适用场景 | 成本 | 复杂度 | 推荐指数 |
|------|---------|------|--------|---------|
| **GitHub Pages** | 开源项目 | 免费 | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| **GitHub Container Registry** | 私有/开源项目 | 免费 | ⭐⭐ 简单 | ⭐⭐⭐⭐⭐ |
| **Harbor** | 企业生产环境 | 自建 | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐⭐ |
| **ChartMuseum** | 小团队 | 自建 | ⭐⭐ 简单 | ⭐⭐⭐ |
| **AWS S3/ECR** | AWS 用户 | 付费 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ |
| **阿里云 OSS/ACR** | 阿里云用户 | 付费 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ |
| **Docker Hub** | 公开项目 | 免费/付费 | ⭐⭐ 简单 | ⭐⭐⭐ |

---

## 🚀 快速开始：发布到 GitHub Pages

### 步骤 1: 创建 GitHub 仓库

```bash
# 在 GitHub 创建新仓库 helm-charts
# 克隆到本地
git clone https://github.com/your-username/helm-charts.git
cd helm-charts
```

### 步骤 2: 打包并发布

```bash
# 复制你的 Chart
cp -r /path/to/AIOps/helm/opsagent .

# 打包 Chart
helm package opsagent
# 输出: Successfully packaged chart and saved it to: opsagent-1.0.0.tgz

# 生成索引文件
helm repo index . --url https://your-username.github.io/helm-charts/

# 提交到 Git
git add .
git commit -m "Add opsagent helm chart v1.0.0"
git push origin main
```

### 步骤 3: 启用 GitHub Pages

1. 进入仓库的 **Settings**
2. 找到 **Pages** 设置
3. Source 选择 **main** branch
4. 目录选择 **/ (root)**
5. 点击 **Save**

### 步骤 4: 使用发布的 Chart

```bash
# 添加你的 Helm 仓库
helm repo add my-charts https://your-username.github.io/helm-charts/

# 更新仓库列表
helm repo update

# 搜索 Chart
helm search repo opsagent

# 安装
helm install opsagent my-charts/opsagent --namespace ops-system --create-namespace

# 查看可用版本
helm search repo opsagent --versions
```

---

## 🚀 快速开始：发布到 GitHub Container Registry

### 步骤 1: 创建 GitHub Token

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. 勾选权限：`write:packages`, `read:packages`
4. 生成并保存 token

### 步骤 2: 登录和推送

```bash
# 登录 GHCR
export CR_PAT=YOUR_TOKEN
echo $CR_PAT | helm registry login ghcr.io -u your-username --password-stdin

# 打包 Chart
cd /path/to/AIOps
helm package ./helm/opsagent

# 推送到 GHCR
helm push opsagent-1.0.0.tgz oci://ghcr.io/your-username

# 成功输出:
# Pushed: ghcr.io/your-username/opsagent:1.0.0
# Digest: sha256:...
```

### 步骤 3: 使用 OCI Chart

```bash
# 安装（不需要添加 repo）
helm install opsagent oci://ghcr.io/your-username/opsagent --version 1.0.0

# 或者先 pull 再安装
helm pull oci://ghcr.io/your-username/opsagent --version 1.0.0
helm install opsagent ./opsagent-1.0.0.tgz
```

---

## 🔄 GitHub Actions 自动发布

创建 `.github/workflows/release-helm.yml`:

```yaml
name: Release Helm Chart

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install Helm
        uses: azure/setup-helm@v3

      - name: Package Helm Chart
        run: |
          helm package ./helm/opsagent

      - name: Login to GitHub Container Registry
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | \
          helm registry login ghcr.io -u ${{ github.actor }} --password-stdin

      - name: Push to GHCR
        run: |
          helm push opsagent-*.tgz oci://ghcr.io/${{ github.repository_owner }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: opsagent-*.tgz
```

使用：

```bash
# 创建 tag 并推送
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# GitHub Actions 会自动发布到 GHCR
```

---

## 📊 使用统计

### 公共 Helm 仓库

- **Artifact Hub**: https://artifacthub.io/
  - 最大的 Helm Chart 搜索平台
  - 聚合了所有主要的公共仓库

- **Bitnami**: https://charts.bitnami.com/bitnami
  - 130+ 个应用
  - 最活跃的社区仓库

- **Helm Stable (已弃用)**:
  - 已迁移到各自独立仓库

### 查找公共 Chart

```bash
# 在 Artifact Hub 搜索
# 访问 https://artifacthub.io/

# 或使用 Helm 搜索
helm search hub nginx
helm search hub postgres
```

---

## 💡 最佳实践

### 1. Chart 版本管理

```yaml
# Chart.yaml
version: 1.0.0      # Chart 版本（遵循 SemVer）
appVersion: "1.0.0" # 应用版本
```

版本规则：
- **MAJOR**: 不兼容的变更
- **MINOR**: 向后兼容的新功能
- **PATCH**: 向后兼容的 bug 修复

### 2. 签名验证（生产环境推荐）

```bash
# 生成密钥对
gpg --full-generate-key

# 签名 Chart
helm package --sign --key 'Your Name' --keyring ~/.gnupg/secring.gpg ./helm/opsagent

# 验证签名
helm verify opsagent-1.0.0.tgz
```

### 3. Chart 依赖管理

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

```bash
# 更新依赖
helm dependency update ./helm/opsagent
```

### 4. 私有仓库认证

```bash
# 添加带认证的仓库
helm repo add my-private-repo https://charts.example.com \
  --username admin \
  --password password

# 或使用 token
helm repo add my-private-repo https://charts.example.com \
  --username token \
  --password $HELM_REPO_TOKEN
```

---

## 🎯 针对你的项目的推荐

根据你的情况，我推荐以下方案：

### 方案 1: GitHub Container Registry（最推荐）

**优点**:
- ✅ 与代码仓库集成
- ✅ 免费
- ✅ 私有/公开灵活切换
- ✅ 与 GitHub Actions 完美集成
- ✅ 不需要额外基础设施

**实施**:
```bash
# 已经为你准备好了上面的步骤
# 只需要创建 GitHub token 并推送即可
```

### 方案 2: GitHub Pages（适合开源）

**优点**:
- ✅ 完全免费
- ✅ 简单易用
- ✅ 适合公开项目

**实施**:
```bash
# 创建单独的 helm-charts 仓库
# 使用上面的步骤发布
```

---

## 📝 完整发布脚本

创建 `scripts/publish-helm.sh`:

```bash
#!/bin/bash
set -e

CHART_PATH="./helm/opsagent"
VERSION=$(grep '^version:' $CHART_PATH/Chart.yaml | awk '{print $2}')

echo "📦 Publishing Helm Chart v$VERSION..."

# 1. Lint
echo "🔍 Linting chart..."
helm lint $CHART_PATH

# 2. Package
echo "📦 Packaging chart..."
helm package $CHART_PATH

# 3. Push to GHCR
echo "🚀 Pushing to GitHub Container Registry..."
helm push opsagent-$VERSION.tgz oci://ghcr.io/$GITHUB_REPOSITORY_OWNER

echo "✅ Chart published successfully!"
echo "📍 Location: oci://ghcr.io/$GITHUB_REPOSITORY_OWNER/opsagent:$VERSION"
echo ""
echo "Install with:"
echo "  helm install opsagent oci://ghcr.io/$GITHUB_REPOSITORY_OWNER/opsagent --version $VERSION"
```

---

**推荐下一步**:

1. 选择存储方案（推荐 GHCR）
2. 配置认证
3. 推送第一个版本
4. 更新文档说明如何使用远程 Chart

需要帮助配置具体的仓库吗？

