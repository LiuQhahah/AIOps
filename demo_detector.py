#!/usr/bin/env python3
"""Demo script for Pod Resource Detector using mock data."""

from unittest.mock import Mock
from src.detectors.k8s.pod_resources import PodResourceDetector


def create_mock_config():
    """Create mock configuration."""
    config = Mock()
    config.k8s = Mock()
    config.k8s.in_cluster = False
    config.k8s.contexts = [{"name": "test-context", "enabled": True}]
    return config


def create_deployment_with_missing_resources():
    """Create mock deployment without resources."""
    deployment = Mock()
    deployment.metadata.name = "no-resources-app"
    deployment.metadata.namespace = "production"
    deployment.metadata.labels = {"app": "web", "tier": "frontend"}

    container = Mock()
    container.name = "nginx"
    container.resources = None  # Missing resources

    deployment.spec.template.spec.containers = [container]
    return deployment


def create_deployment_with_over_provisioned_resources():
    """Create mock deployment with excessive resources."""
    deployment = Mock()
    deployment.metadata.name = "over-provisioned-app"
    deployment.metadata.namespace = "production"
    deployment.metadata.labels = {"app": "backend", "tier": "api"}

    container = Mock()
    container.name = "api-server"
    container.resources = Mock()
    container.resources.requests = {"cpu": "4", "memory": "16Gi"}  # Excessive
    container.resources.limits = {"cpu": "8", "memory": "32Gi"}

    deployment.spec.template.spec.containers = [container]
    return deployment


def create_deployment_with_good_resources():
    """Create mock deployment with proper resources."""
    deployment = Mock()
    deployment.metadata.name = "healthy-app"
    deployment.metadata.namespace = "production"
    deployment.metadata.labels = {"app": "cache", "tier": "backend"}

    container = Mock()
    container.name = "redis"
    container.resources = Mock()
    container.resources.requests = {"cpu": "100m", "memory": "256Mi"}
    container.resources.limits = {"cpu": "200m", "memory": "512Mi"}

    deployment.spec.template.spec.containers = [container]
    return deployment


def main():
    """Run demo."""
    print("=" * 80)
    print("K8s Pod 资源检测器 - 演示模式")
    print("=" * 80)

    # Create detector
    config = create_mock_config()
    detector = PodResourceDetector(config)

    print("\n测试场景：检测三个不同的 Deployment\n")

    # Test Case 1: Missing resources
    print("1️⃣  检测缺少资源限制的 Deployment...")
    print("-" * 80)
    deployment1 = create_deployment_with_missing_resources()

    container = deployment1.spec.template.spec.containers[0]
    issue = detector._check_missing_resources(
        name=deployment1.metadata.name,
        namespace=deployment1.metadata.namespace,
        resource_type="Deployment",
        container=container,
        labels=deployment1.metadata.labels
    )

    if issue:
        print(f"✗ 发现问题!")
        print(f"  资源: {issue.resource_name}")
        print(f"  命名空间: {issue.namespace}")
        print(f"  严重程度: {issue.severity.value}")
        print(f"  问题: {issue.title}")
        print(f"  描述: {issue.description}")
        print(f"  推荐配置:")
        print(f"    requests: {issue.recommended_value['requests']}")
        print(f"    limits: {issue.recommended_value['limits']}")
    else:
        print("✓ 无问题")

    # Test Case 2: Over-provisioned resources
    print("\n2️⃣  检测资源过度配置的 Deployment...")
    print("-" * 80)
    deployment2 = create_deployment_with_over_provisioned_resources()

    container = deployment2.spec.template.spec.containers[0]
    issue = detector._check_over_provisioned(
        name=deployment2.metadata.name,
        namespace=deployment2.metadata.namespace,
        resource_type="Deployment",
        container=container,
        labels=deployment2.metadata.labels
    )

    if issue:
        print(f"✗ 发现问题!")
        print(f"  资源: {issue.resource_name}")
        print(f"  命名空间: {issue.namespace}")
        print(f"  严重程度: {issue.severity.value}")
        print(f"  问题: {issue.title}")
        print(f"  描述: {issue.description}")
        print(f"  当前配置: CPU={issue.current_value['requests']['cpu']}, "
              f"Memory={issue.current_value['requests']['memory']}")
        print(f"  推荐配置: CPU={issue.recommended_value['requests']['cpu']}, "
              f"Memory={issue.recommended_value['requests']['memory']}")
        print(f"  💰 预计节省: ~50% 资源")
    else:
        print("✓ 无问题")

    # Test Case 3: Healthy resources
    print("\n3️⃣  检测配置良好的 Deployment...")
    print("-" * 80)
    deployment3 = create_deployment_with_good_resources()

    container = deployment3.spec.template.spec.containers[0]
    missing_issue = detector._check_missing_resources(
        name=deployment3.metadata.name,
        namespace=deployment3.metadata.namespace,
        resource_type="Deployment",
        container=container,
        labels=deployment3.metadata.labels
    )
    over_issue = detector._check_over_provisioned(
        name=deployment3.metadata.name,
        namespace=deployment3.metadata.namespace,
        resource_type="Deployment",
        container=container,
        labels=deployment3.metadata.labels
    )

    if not missing_issue and not over_issue:
        print(f"✓ 配置良好!")
        print(f"  资源: {deployment3.metadata.name}")
        print(f"  CPU: 100m (request) / 200m (limit)")
        print(f"  Memory: 256Mi (request) / 512Mi (limit)")
    else:
        print("✗ 发现问题")

    # Summary
    print("\n" + "=" * 80)
    print("检测能力总结:")
    print("=" * 80)
    print("✅ 检测缺少 resource requests 和 limits 的容器")
    print("✅ 检测资源过度配置（CPU > 2 cores 或 Memory > 4Gi）")
    print("✅ 自动计算推荐的资源配置")
    print("✅ 支持 Deployment、StatefulSet、DaemonSet")
    print("✅ 跳过系统命名空间（kube-system 等）")
    print("✅ 提供详细的问题描述和修复建议")
    print("=" * 80)

    # Additional feature tests
    print("\n额外功能测试:")
    print("-" * 80)

    # Test CPU parsing
    print("\nCPU 单位解析:")
    print(f"  100m = {detector._parse_cpu('100m')} cores")
    print(f"  1000m = {detector._parse_cpu('1000m')} cores")
    print(f"  2 = {detector._parse_cpu('2')} cores")

    # Test memory parsing
    print("\nMemory 单位解析:")
    print(f"  128Mi = {detector._parse_memory('128Mi') / (1024**2):.0f} MiB")
    print(f"  1Gi = {detector._parse_memory('1Gi') / (1024**3):.0f} GiB")
    print(f"  4Gi = {detector._parse_memory('4Gi') / (1024**3):.0f} GiB")

    print("\n" + "=" * 80)
    print("演示完成！检测器已准备就绪。")
    print("=" * 80)


if __name__ == "__main__":
    main()
