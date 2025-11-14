# Self-Hosted Runner 快速开始指南

5 分钟完成 Self-Hosted Runner 的安装和配置！

## 🚀 快速安装（Linux）

### 步骤 1: 获取安装命令（2 分钟）

1. 在 GitHub 仓库中: **Settings** → **Actions** → **Runners** → **New self-hosted runner**
2. 选择 **Linux**
3. 复制显示的安装命令

### 步骤 2: 在服务器上安装（3 分钟）

```bash
# SSH 登录到你的服务器
ssh user@your-server

# 执行 GitHub 显示的安装命令
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# 配置 runner（使用 GitHub 页面显示的 token）
./config.sh --url https://github.com/YOUR_USERNAME/YOUR_REPO --token YOUR_TOKEN

# 提示输入时：
# - Runner name: 输入 "k8s-runner" (或你喜欢的名字)
# - 其他选项: 全部按回车使用默认值

# 安装为服务（这样 runner 会一直运行）
sudo ./svc.sh install
sudo ./svc.sh start

# 验证状态
sudo ./svc.sh status
```

### 步骤 3: 安装必要工具

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# 安装 kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/

# 重启 runner 服务使权限生效
sudo ./svc.sh stop && sudo ./svc.sh start
```

### 步骤 4: 配置 Kubernetes 访问

```bash
# 创建 .kube 目录
mkdir -p ~/.kube

# 从本地复制 kubeconfig（在你的本地机器上运行）
scp ~/.kube/config user@your-server:~/.kube/config

# 或者直接在服务器上创建
nano ~/.kube/config
# 粘贴你的 kubeconfig 内容，保存

# 设置权限
chmod 600 ~/.kube/config

# 测试连接
kubectl cluster-info
kubectl get nodes
```

## ✅ 验证安装

### 在 GitHub 上验证

1. 回到 GitHub: **Settings** → **Actions** → **Runners**
2. 应该看到你的 runner，状态为 **Idle** (绿色圆点)

### 运行测试

创建测试文件 `.github/workflows/test-runner.yml`:

```yaml
name: Test Runner
on: workflow_dispatch

jobs:
  test:
    runs-on: self-hosted
    steps:
      - name: Test environment
        run: |
          echo "✅ Runner is working!"
          docker --version
          kubectl version --client
          kubectl get nodes
```

然后在 GitHub Actions 页面手动运行这个 workflow。

## 🎯 开始使用

现在你可以使用新的 self-hosted workflow：

```bash
# 确保 deploy-self-hosted.yml 已创建
ls .github/workflows/deploy-self-hosted.yml

# 推送代码到 main 分支触发部署
git add .
git commit -m "Deploy with self-hosted runner"
git push origin main

# 在 GitHub Actions 查看部署进度
```

## 📋 重要配置检查清单

- [ ] Runner 状态显示为 "Idle"
- [ ] Docker 已安装并可以无 sudo 使用
- [ ] kubectl 可以连接到 K8s 集群
- [ ] Runner 作为服务运行（会自动启动）
- [ ] kubeconfig 文件权限正确 (600)

## ⚠️ 安全提醒

1. **仅在私有仓库使用 self-hosted runner**
2. 不要使用 root 用户运行 runner
3. 定期更新 runner 和操作系统
4. 使用受限的 kubeconfig（不要用 cluster-admin）

## 🔧 常用命令

```bash
# 查看 runner 状态
sudo systemctl status actions.runner.*.service

# 停止 runner
sudo ./svc.sh stop

# 启动 runner
sudo ./svc.sh start

# 重启 runner
sudo ./svc.sh restart

# 查看 runner 日志
sudo journalctl -u actions.runner.*.service -f

# 清理 Docker 镜像（节省空间）
docker system prune -a -f
```

## 📚 下一步

- 阅读完整文档: [SELF_HOSTED_RUNNER_SETUP.md](./SELF_HOSTED_RUNNER_SETUP.md)
- 配置监控和告警
- 设置自动清理任务
- 优化性能和安全性

## 🆘 遇到问题？

### Runner 显示 Offline
```bash
sudo systemctl restart actions.runner.*.service
```

### Docker 权限错误
```bash
sudo usermod -aG docker $USER
# 然后重新登录或重启服务
```

### kubectl 连接失败
```bash
# 检查 kubeconfig
kubectl cluster-info
# 如果失败，验证文件路径和内容
cat ~/.kube/config
```

详细故障排查: [SELF_HOSTED_RUNNER_SETUP.md#故障排查](./SELF_HOSTED_RUNNER_SETUP.md#故障排查)

---

**就这么简单！** 🎉

你的 CI/CD 流水线现在运行在自己的基础设施上了！
