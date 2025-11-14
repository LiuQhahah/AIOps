# Self-Hosted Runner 安装配置指南

本文档说明如何设置 GitHub Actions Self-Hosted Runner 来运行 CI/CD 流水线。

## 📋 目录

- [什么是 Self-Hosted Runner](#什么是-self-hosted-runner)
- [优势与劣势](#优势与劣势)
- [前置要求](#前置要求)
- [安装步骤](#安装步骤)
- [配置指南](#配置指南)
- [安全考虑](#安全考虑)
- [故障排查](#故障排查)

## 什么是 Self-Hosted Runner

Self-Hosted Runner 是运行在你自己基础设施上的 GitHub Actions 执行器，而不是使用 GitHub 提供的云端 runner。

### 架构对比

```
GitHub-Hosted Runner:
┌──────────┐       ┌──────────────────┐       ┌─────────────┐
│  GitHub  │  -->  │  GitHub Runner   │  -->  │   K8s 集群  │
│  Actions │       │  (GitHub Cloud)  │       │  (你的)     │
└──────────┘       └──────────────────┘       └─────────────┘
                   需要公网访问

Self-Hosted Runner:
┌──────────┐       ┌──────────────────┐       ┌─────────────┐
│  GitHub  │  -->  │  Self-Hosted     │  -->  │   K8s 集群  │
│  Actions │       │  Runner (你的)   │       │  (同一网络) │
└──────────┘       └──────────────────┘       └─────────────┘
                   可以在内网运行
```

## 优势与劣势

### ✅ 优势

1. **私有网络访问** - 可以访问内网的 Kubernetes 集群，无需暴露公网
2. **无限分钟数** - 不受 GitHub Actions 免费分钟数限制
3. **自定义环境** - 预装你需要的所有工具
4. **更快的构建** - 无需每次下载依赖，可以使用本地缓存
5. **本地 Docker 镜像** - 可以使用本地 registry，无需推送到公网
6. **更大的资源** - 可以使用更强大的机器

### ❌ 劣势

1. **需要维护** - 你负责维护和更新 runner
2. **安全风险** - 需要自己管理安全性
3. **成本** - 需要提供运行环境（服务器/虚拟机）
4. **可用性** - 你负责确保 runner 一直在线

## 前置要求

### 硬件要求

| 资源 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 20 GB | 50 GB+ (SSD) |
| 网络 | 访问 GitHub.com | 稳定连接 |

### 软件要求

- **操作系统**: Linux (Ubuntu 20.04+), macOS, Windows Server
- **Docker**: 用于构建镜像
- **kubectl**: 用于部署到 Kubernetes
- **Git**: GitHub Actions Runner 依赖

### 网络要求

- 可以访问 GitHub.com (HTTPS)
- 可以访问你的 Kubernetes 集群
- 可以访问 Docker registry (如果需要推送镜像)

## 安装步骤

### 方法 1: 在 Linux 服务器上安装 (推荐)

#### 步骤 1: 获取 Runner Token

1. 进入你的 GitHub 仓库
2. 点击 `Settings` → `Actions` → `Runners`
3. 点击 `New self-hosted runner`
4. 选择操作系统 (Linux)
5. 复制显示的安装命令

#### 步骤 2: 安装 Runner

在你的服务器上运行以下命令：

```bash
# 创建 runner 目录
mkdir -p ~/actions-runner && cd ~/actions-runner

# 下载最新版本的 runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# 解压
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# 配置 runner (使用 GitHub 页面显示的命令)
./config.sh --url https://github.com/YOUR_USERNAME/YOUR_REPO \
  --token YOUR_TOKEN

# 配置过程中的选项:
# - Runner group: 按回车使用默认
# - Runner name: 输入名称，如 "k8s-runner-1"
# - Runner labels: 按回车使用默认，或添加自定义标签
# - Work folder: 按回车使用默认

# 启动 runner (交互式)
./run.sh

# 或者作为服务运行 (推荐)
sudo ./svc.sh install
sudo ./svc.sh start
```

#### 步骤 3: 安装必要的工具

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 将 runner 用户添加到 docker 组
sudo usermod -aG docker $USER

# 安装 kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 验证安装
docker --version
kubectl version --client
```

#### 步骤 4: 配置 kubectl 访问集群

```bash
# 创建 .kube 目录
mkdir -p ~/.kube

# 复制你的 kubeconfig 文件
# 方式 1: 从本地复制
scp ~/.kube/config user@runner-server:~/.kube/config

# 方式 2: 直接创建
cat > ~/.kube/config <<'EOF'
# 粘贴你的 kubeconfig 内容
EOF

# 设置权限
chmod 600 ~/.kube/config

# 验证连接
kubectl cluster-info
kubectl get nodes
```

### 方法 2: 在 Kubernetes 集群中运行 Runner

如果你想在 K8s 集群内运行 runner，可以使用 [actions-runner-controller](https://github.com/actions/actions-runner-controller):

```bash
# 安装 cert-manager (前置要求)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 安装 actions-runner-controller
kubectl apply -f https://github.com/actions/actions-runner-controller/releases/latest/download/actions-runner-controller.yaml

# 创建 runner deployment
cat <<EOF | kubectl apply -f -
apiVersion: actions.summerwind.dev/v1alpha1
kind: RunnerDeployment
metadata:
  name: github-runner
  namespace: actions-runner-system
spec:
  replicas: 1
  template:
    spec:
      repository: YOUR_USERNAME/YOUR_REPO
      env:
        - name: DOCKER_ENABLED
          value: "true"
EOF
```

### 方法 3: 使用 Docker 运行 Runner

```bash
# 拉取官方镜像
docker pull myoung34/github-runner:latest

# 运行 runner
docker run -d \
  --name github-runner \
  --restart always \
  -e REPO_URL="https://github.com/YOUR_USERNAME/YOUR_REPO" \
  -e ACCESS_TOKEN="YOUR_GITHUB_TOKEN" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.kube:/home/runner/.kube \
  myoung34/github-runner:latest
```

## 配置指南

### 配置 1: 基本配置

Runner 安装完成后，在 GitHub 仓库中验证：

```
Settings → Actions → Runners → 查看你的 runner 状态
应该显示为 "Idle" (绿色)
```

### 配置 2: 环境变量

为 runner 设置环境变量（如果作为服务运行）：

```bash
# 编辑服务文件
sudo nano /etc/systemd/system/actions.runner.*.service

# 在 [Service] 部分添加:
[Service]
Environment="DOCKER_HOST=unix:///var/run/docker.sock"
Environment="KUBECONFIG=/home/runner/.kube/config"

# 重新加载并重启
sudo systemctl daemon-reload
sudo systemctl restart actions.runner.*.service
```

### 配置 3: 使用本地 Docker Registry (可选)

如果不想推送镜像到公网，可以使用本地 registry：

```bash
# 在 runner 所在服务器运行本地 registry
docker run -d -p 5000:5000 --restart=always --name registry registry:2

# 修改 workflow 中的 REGISTRY 环境变量
# env:
#   REGISTRY: localhost:5000
#   IMAGE_NAME: opsagent

# 在 K8s 集群中配置 insecure registry (如果使用 HTTP)
# 编辑 /etc/docker/daemon.json
{
  "insecure-registries": ["runner-server:5000"]
}
```

### 配置 4: 自动更新 Runner

```bash
# 创建更新脚本
cat > ~/update-runner.sh <<'EOF'
#!/bin/bash
cd ~/actions-runner
./svc.sh stop
./config.sh remove --token YOUR_REMOVAL_TOKEN
curl -o actions-runner-linux-x64.tar.gz -L \
  https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64.tar.gz
./config.sh --url https://github.com/YOUR_USERNAME/YOUR_REPO --token YOUR_TOKEN
./svc.sh install
./svc.sh start
EOF

chmod +x ~/update-runner.sh

# 添加到 crontab (每月检查)
# crontab -e
# 0 0 1 * * ~/update-runner.sh
```

## 验证 Runner 配置

### 测试 1: 验证 Runner 状态

```bash
# 检查 runner 服务状态
sudo systemctl status actions.runner.*.service

# 查看 runner 日志
sudo journalctl -u actions.runner.*.service -f
```

### 测试 2: 运行测试 Workflow

创建一个简单的测试 workflow：

```yaml
# .github/workflows/test-runner.yml
name: Test Self-Hosted Runner

on: workflow_dispatch

jobs:
  test:
    runs-on: self-hosted
    steps:
      - name: Test environment
        run: |
          echo "Runner hostname: $(hostname)"
          echo "Docker version: $(docker --version)"
          echo "Kubectl version: $(kubectl version --client)"
          echo "Kubernetes cluster:"
          kubectl cluster-info
```

运行这个 workflow 来验证 runner 配置是否正确。

### 测试 3: 完整部署测试

使用新创建的 `deploy-self-hosted.yml` workflow 进行完整测试：

```bash
# 推送代码到 main 分支
git add .
git commit -m "Test self-hosted runner deployment"
git push origin main

# 在 GitHub Actions 页面查看执行结果
```

## 安全考虑

### ⚠️ 重要安全建议

1. **不要在公共仓库使用 self-hosted runner**
   - Self-hosted runner 可以被 PR 触发
   - 恶意代码可能在你的服务器上执行
   - 仅在私有仓库使用

2. **使用专用账号运行 runner**
   ```bash
   # 创建专用用户
   sudo useradd -m -s /bin/bash github-runner
   sudo su - github-runner
   # 然后再安装 runner
   ```

3. **限制 runner 权限**
   - 不要使用 root 用户运行
   - 使用最小权限原则配置 kubeconfig
   - 考虑使用 ServiceAccount Token 而不是完整的 kubeconfig

4. **网络隔离**
   ```bash
   # 使用防火墙限制出站连接
   sudo ufw allow out to api.github.com port 443
   sudo ufw allow out to your-k8s-api-server port 6443
   ```

5. **定期更新**
   - 保持 runner 软件最新
   - 定期更新操作系统和 Docker

6. **监控和审计**
   ```bash
   # 监控 runner 日志
   sudo journalctl -u actions.runner.*.service -f | tee -a runner-audit.log
   ```

### 推荐的 kubeconfig 配置

不要使用完整的管理员 kubeconfig，而是创建受限的 ServiceAccount：

```bash
# 创建 ServiceAccount
kubectl create serviceaccount github-runner -n ops-system

# 创建 Role (仅限 ops-system namespace)
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: github-runner-role
  namespace: ops-system
rules:
- apiGroups: ["", "apps"]
  resources: ["deployments", "services", "configmaps", "secrets", "pods"]
  verbs: ["get", "list", "create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
EOF

# 创建 RoleBinding
kubectl create rolebinding github-runner-binding \
  --role=github-runner-role \
  --serviceaccount=ops-system:github-runner \
  -n ops-system

# 创建受限的 kubeconfig
# (参考 GITHUB_ACTIONS_SETUP.md 中的 ServiceAccount 方法)
```

## 故障排查

### 问题 1: Runner 显示 Offline

**解决方案**:
```bash
# 检查服务状态
sudo systemctl status actions.runner.*.service

# 重启服务
sudo systemctl restart actions.runner.*.service

# 查看日志
sudo journalctl -u actions.runner.*.service -n 100
```

### 问题 2: Docker 权限错误

**错误**: `permission denied while trying to connect to the Docker daemon socket`

**解决方案**:
```bash
# 将 runner 用户添加到 docker 组
sudo usermod -aG docker $(whoami)

# 重启 runner 服务
sudo systemctl restart actions.runner.*.service
```

### 问题 3: kubectl 无法连接集群

**解决方案**:
```bash
# 检查 kubeconfig
cat ~/.kube/config

# 测试连接
kubectl cluster-info

# 检查环境变量
echo $KUBECONFIG

# 如果作为服务运行，确保服务可以访问 kubeconfig
sudo -u runner kubectl cluster-info
```

### 问题 4: Workflow 不使用 self-hosted runner

**解决方案**:
```yaml
# 确保 workflow 中指定了 self-hosted
jobs:
  build:
    runs-on: self-hosted  # 必须是这个

# 如果使用了自定义标签
jobs:
  build:
    runs-on: [self-hosted, linux, x64]
```

### 问题 5: 磁盘空间不足

**解决方案**:
```bash
# 清理 Docker 镜像和容器
docker system prune -a -f

# 清理 runner 工作目录
cd ~/actions-runner/_work
rm -rf ./*

# 设置自动清理 (添加到 crontab)
0 2 * * * docker system prune -a -f
```

## 维护任务

### 日常维护

```bash
# 每周检查
- 查看 runner 状态和日志
- 检查磁盘空间
- 清理 Docker 镜像

# 每月维护
- 更新系统软件包
- 更新 Docker
- 检查 runner 版本更新

# 季度维护
- 审查安全设置
- 更新 kubeconfig
- 检查并更新依赖
```

### 备份 Runner 配置

```bash
# 备份配置
mkdir -p ~/runner-backup
cp -r ~/actions-runner/.credentials ~/runner-backup/
cp ~/.kube/config ~/runner-backup/kubeconfig
cp /etc/systemd/system/actions.runner.*.service ~/runner-backup/

# 备份环境变量
env | grep -E '(DOCKER|KUBE)' > ~/runner-backup/env.txt
```

## 性能优化

### 1. 使用 SSD 存储

```bash
# 将 runner 工作目录移动到 SSD
sudo mv ~/actions-runner /mnt/ssd/actions-runner
ln -s /mnt/ssd/actions-runner ~/actions-runner
```

### 2. 配置 Docker 缓存

```bash
# 编辑 /etc/docker/daemon.json
{
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 10,
  "storage-driver": "overlay2"
}

sudo systemctl restart docker
```

### 3. 使用本地依赖缓存

```yaml
# 在 workflow 中使用本地缓存
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      ~/.npm
    key: ${{ runner.os }}-deps-${{ hashFiles('**/requirements.txt') }}
```

## 监控 Runner

### 基本监控

```bash
# 创建监控脚本
cat > ~/monitor-runner.sh <<'EOF'
#!/bin/bash
echo "=== Runner Status ==="
sudo systemctl status actions.runner.*.service | grep Active

echo ""
echo "=== Disk Usage ==="
df -h | grep -E '(Filesystem|/dev/)'

echo ""
echo "=== Docker Images ==="
docker images | wc -l
echo "Total images"

echo ""
echo "=== Memory Usage ==="
free -h
EOF

chmod +x ~/monitor-runner.sh
```

### 集成 Prometheus (可选)

安装 node_exporter 来监控 runner 服务器：

```bash
# 下载并安装 node_exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xzf node_exporter-1.7.0.linux-amd64.tar.gz
sudo mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/

# 创建 systemd 服务
sudo tee /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Node Exporter

[Service]
User=nobody
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

## 相关资源

- [GitHub Self-Hosted Runners 官方文档](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Actions Runner Controller](https://github.com/actions/actions-runner-controller)
- [Runner 安全最佳实践](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

## 总结

使用 Self-Hosted Runner 的关键点：

1. ✅ 确保 runner 有足够的资源
2. ✅ 正确配置 Docker 和 kubectl
3. ✅ 使用专用账号和最小权限
4. ✅ 定期维护和更新
5. ✅ 监控 runner 状态
6. ⚠️ 仅在私有仓库使用
7. ⚠️ 注意安全风险

---

**文档版本**: 1.0.0
**最后更新**: 2024年
**状态**: ✅ 生产就绪
