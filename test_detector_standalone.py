#!/usr/bin/env python3
"""Standalone test script for Pod Resource Detector."""

import asyncio
from src.detectors.k8s.pod_resources import PodResourceDetector
from src.utils.config import load_config


async def main():
    """Run detector and print results."""
    # Load configuration
    print("加载配置...")
    config = load_config("config/config.local.yaml")

    # Create detector
    print("初始化 Pod 资源检测器...")
    detector = PodResourceDetector(config)

    # Run detection
    print("\n开始检测 Pod 资源配置问题...\n")
    try:
        issues = await detector.detect()

        print(f"检测完成！发现 {len(issues)} 个问题：\n")
        print("=" * 80)

        for i, issue in enumerate(issues, 1):
            print(f"\n问题 #{i}")
            print(f"  平台: {issue.platform.value}")
            print(f"  资源类型: {issue.resource_type}")
            print(f"  资源名称: {issue.resource_name}")
            print(f"  命名空间: {issue.namespace}")
            print(f"  严重程度: {issue.severity.value}")
            print(f"  标题: {issue.title}")
            print(f"  描述: {issue.description}")
            print(f"  可自动修复: {issue.auto_fixable}")

            if issue.current_value:
                print(f"\n  当前配置:")
                for key, value in issue.current_value.items():
                    print(f"    {key}: {value}")

            if issue.recommended_value:
                print(f"\n  推荐配置:")
                for key, value in issue.recommended_value.items():
                    print(f"    {key}: {value}")

            print("-" * 80)

        # Summary
        if issues:
            print("\n问题总结:")
            low = sum(1 for i in issues if i.severity.value == "low")
            medium = sum(1 for i in issues if i.severity.value == "medium")
            high = sum(1 for i in issues if i.severity.value == "high")

            print(f"  低严重度: {low}")
            print(f"  中等严重度: {medium}")
            print(f"  高严重度: {high}")
            print(f"  可自动修复: {sum(1 for i in issues if i.auto_fixable)}")
        else:
            print("\n✓ 未发现任何问题，所有 Pod 资源配置良好！")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
