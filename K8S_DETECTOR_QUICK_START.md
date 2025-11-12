# K8s Pod 资源检测器 - 快速开始指南

## 🚀 快速开始

### 1. 运行演示（无需 K8s 集群）

```bash
source .venv/bin/activate
python demo_detector.py
```

这将展示检测器如何：
- ✅ 检测缺少资源限制的 Pod
- ✅ 检测资源过度配置的 Pod
- ✅ 提供智能推荐配置

### 2. 运行单元测试

```bash
source .venv/bin/activate
python -m pytest tests/unit/detectors/test_pod_resources.py -v
```

预期输出：`23 passed`

### 3. 连接真实 K8s 集群

```bash
# 确保 kubectl 可以访问集群
kubectl get nodes

# 运行检测器
source .venv/bin/activate
python test_detector_standalone.py
```

## 📋 检测能力

### 自动检测的问题类型

| 问题类型 | 严重程度 | 自动修复 | 检测条件 |
|---------|---------|---------|---------|
| 缺少 resource requests | MEDIUM | ✅ | container.resources.requests 为空 |
| 缺少 resource limits | MEDIUM | ✅ | container.resources.limits 为空 |
| CPU 过度配置 | LOW | ✅ | CPU request > 2 cores |
| Memory 过度配置 | LOW | ✅ | Memory request > 4Gi |

### 支持的资源类型

- ✅ **Deployment** - 应用部署
- ✅ **StatefulSet** - 有状态应用
- ✅ **DaemonSet** - 守护进程

### 跳过的命名空间

自动跳过系统命名空间：
- `kube-system`
- `kube-public`
- `kube-node-lease`
- `local-path-storage`

## 🔧 配置

### 默认推荐值

```python
# 对于缺少资源限制的容器
CPU request: 100m
CPU limit: 200m
Memory request: 128Mi
Memory limit: 256Mi
```

### 过度配置阈值

```python
CPU threshold: 2.0 cores
Memory threshold: 4Gi
```

### 自定义配置

编辑 `src/detectors/k8s/pod_resources.py`：

```python
class PodResourceDetector(BaseDetector):
    # 修改这些类变量来自定义阈值
    OVER_PROVISIONED_CPU_THRESHOLD = 2.0
    OVER_PROVISIONED_MEMORY_THRESHOLD = 4 * 1024 * 1024 * 1024

    # 修改默认推荐值
    DEFAULT_CPU_REQUEST = "100m"
    DEFAULT_CPU_LIMIT = "200m"
    DEFAULT_MEMORY_REQUEST = "128Mi"
    DEFAULT_MEMORY_LIMIT = "256Mi"
```

## 📊 检测输出示例

### 场景 1：缺少资源限制

```
问题 #1
  平台: k8s
  资源类型: Deployment
  资源名称: nginx-app
  命名空间: production
  严重程度: medium
  标题: Missing resource requests/limits
  描述: Container 'nginx' in Deployment 'nginx-app' is missing resource
        requests/limits. This can lead to unpredictable scheduling and
        potential resource contention.
  可自动修复: True

  推荐配置:
    requests: {'cpu': '100m', 'memory': '128Mi'}
    limits: {'cpu': '200m', 'memory': '256Mi'}
```

### 场景 2：资源过度配置

```
问题 #2
  平台: k8s
  资源类型: Deployment
  资源名称: api-server
  命名空间: production
  严重程度: low
  标题: Over-provisioned resources
  描述: Container 'app' in Deployment 'api-server' has excessive resource
        requests (CPU: 4, Memory: 16Gi). Consider reducing to optimize
        cluster utilization.
  可自动修复: True

  当前配置:
    container: app
    requests: {'cpu': '4', 'memory': '16Gi'}

  推荐配置:
    requests: {'cpu': '2000m', 'memory': '8192Mi'}
    limits: {'cpu': '4000m', 'memory': '16384Mi'}
```

## 🧪 测试覆盖

### 单元测试清单 (23 个测试)

✅ 基础功能测试
- `test_platform_property` - 验证平台为 K8S
- `test_resource_type_property` - 验证资源类型为 Pod

✅ 资源解析测试
- `test_parse_cpu_millicores` - CPU millicores 解析
- `test_parse_cpu_cores` - CPU cores 解析
- `test_parse_memory_ki` - 内存 Ki 单位解析
- `test_parse_memory_mi` - 内存 Mi 单位解析
- `test_parse_memory_gi` - 内存 Gi 单位解析
- `test_parse_memory_bytes` - 内存字节解析

✅ 命名空间过滤测试
- `test_should_skip_namespace_system` - 跳过系统命名空间
- `test_should_skip_namespace_user` - 不跳过用户命名空间

✅ 缺少资源检测测试
- `test_check_missing_resources_both_missing` - 同时缺少 requests 和 limits
- `test_check_missing_resources_requests_missing` - 只缺少 requests
- `test_check_missing_resources_limits_missing` - 只缺少 limits
- `test_check_missing_resources_all_present` - 配置完整

✅ 过度配置检测测试
- `test_check_over_provisioned_cpu` - CPU 过度配置
- `test_check_over_provisioned_memory` - Memory 过度配置
- `test_check_over_provisioned_normal_resources` - 正常资源配置
- `test_check_over_provisioned_no_requests` - 无 requests 配置

✅ 集成测试
- `test_check_deployments_with_issues` - Deployment 检测
- `test_check_deployments_skip_system_namespace` - 跳过系统命名空间

✅ 工具函数测试
- `test_resource_to_dict` - 资源字典转换
- `test_resource_to_dict_none` - 空资源处理
- `test_recommended_values_for_missing_resources` - 推荐值验证

## 🐛 故障排查

### 问题：无法连接到 K8s 集群

```bash
# 检查 kubectl 配置
kubectl cluster-info

# 检查当前上下文
kubectl config current-context

# 列出所有上下文
kubectl config get-contexts
```

### 问题：导入错误

```bash
# 重新安装依赖
source .venv/bin/activate
pip install -e ".[dev]"
```

### 问题：测试失败

```bash
# 查看详细输出
python -m pytest tests/unit/detectors/test_pod_resources.py -v -s

# 只运行失败的测试
python -m pytest tests/unit/detectors/test_pod_resources.py --lf
```

## 📝 代码示例

### 直接使用检测器

```python
from src.detectors.k8s.pod_resources import PodResourceDetector
from src.utils.config import load_config

# 加载配置
config = load_config("config/config.local.yaml")

# 创建检测器
detector = PodResourceDetector(config)

# 运行检测
issues = await detector.detect()

# 处理结果
for issue in issues:
    print(f"发现问题: {issue.title}")
    print(f"资源: {issue.resource_name}")
    print(f"推荐: {issue.recommended_value}")
```

### 集成到检测引擎

检测器已自动集成到 `DetectionEngine`，无需额外配置：

```python
from src.core.detection_engine import DetectionEngine
from src.utils.config import load_config

config = load_config("config/config.yaml")
engine = DetectionEngine(config)

# 运行所有检测器（包括 Pod 资源检测器）
issues = await engine.run_detection()
```

## 🔗 相关文件

| 文件 | 说明 |
|------|------|
| `src/detectors/k8s/pod_resources.py` | 检测器核心实现 (385 行) |
| `tests/unit/detectors/test_pod_resources.py` | 单元测试 (304 行) |
| `demo_detector.py` | 功能演示脚本 |
| `test_detector_standalone.py` | 真实集群测试脚本 |
| `IMPLEMENTATION_SUMMARY.md` | 完整实现总结 |

## ✨ 下一步

检测器已准备就绪！接下来可以：

1. **阶段2**: 实现 YAML 修复和 GitOps 集成
2. **可选**: 添加 Prometheus 集成用于智能推荐
3. **可选**: 支持自定义检测规则
4. **可选**: 生成 HTML/PDF 检测报告

## 📞 技术支持

如遇问题，请检查：
1. 依赖是否正确安装
2. Kubernetes 集群是否可访问
3. 配置文件是否正确
4. 查看日志输出获取详细错误信息

---

**状态**: ✅ 已完成并测试
**版本**: 1.0.0
**最后更新**: 2024年
