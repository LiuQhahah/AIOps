"""Unit tests for PodResourceDetector."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any

from src.detectors.k8s.pod_resources import PodResourceDetector
from src.detectors.base.detector import Platform, Severity


class TestPodResourceDetector:
    """Test suite for PodResourceDetector."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock()
        config.k8s = Mock()
        config.k8s.in_cluster = False
        config.k8s.contexts = [{"name": "test-context", "enabled": True}]
        return config

    @pytest.fixture
    def detector(self, mock_config):
        """Create detector instance."""
        return PodResourceDetector(mock_config)

    def test_platform_property(self, detector):
        """Test platform property returns K8S."""
        assert detector.platform == Platform.K8S

    def test_resource_type_property(self, detector):
        """Test resource_type property returns Pod."""
        assert detector.resource_type == "Pod"

    def test_parse_cpu_millicores(self, detector):
        """Test CPU parsing with millicores."""
        assert detector._parse_cpu("100m") == 0.1
        assert detector._parse_cpu("500m") == 0.5
        assert detector._parse_cpu("1000m") == 1.0

    def test_parse_cpu_cores(self, detector):
        """Test CPU parsing with cores."""
        assert detector._parse_cpu("1") == 1.0
        assert detector._parse_cpu("2.5") == 2.5
        assert detector._parse_cpu("0.5") == 0.5

    def test_parse_memory_ki(self, detector):
        """Test memory parsing with Ki suffix."""
        assert detector._parse_memory("100Ki") == 100 * 1024
        assert detector._parse_memory("1Ki") == 1024

    def test_parse_memory_mi(self, detector):
        """Test memory parsing with Mi suffix."""
        assert detector._parse_memory("128Mi") == 128 * 1024 * 1024
        assert detector._parse_memory("256Mi") == 256 * 1024 * 1024

    def test_parse_memory_gi(self, detector):
        """Test memory parsing with Gi suffix."""
        assert detector._parse_memory("1Gi") == 1024 * 1024 * 1024
        assert detector._parse_memory("4Gi") == 4 * 1024 * 1024 * 1024

    def test_parse_memory_bytes(self, detector):
        """Test memory parsing with no suffix (bytes)."""
        assert detector._parse_memory("1024") == 1024
        assert detector._parse_memory("2048") == 2048

    def test_should_skip_namespace_system(self, detector):
        """Test skipping system namespaces."""
        assert detector._should_skip_namespace("kube-system") is True
        assert detector._should_skip_namespace("kube-public") is True
        assert detector._should_skip_namespace("kube-node-lease") is True
        assert detector._should_skip_namespace("local-path-storage") is True

    def test_should_skip_namespace_user(self, detector):
        """Test not skipping user namespaces."""
        assert detector._should_skip_namespace("default") is False
        assert detector._should_skip_namespace("test-app") is False
        assert detector._should_skip_namespace("production") is False

    def test_check_missing_resources_both_missing(self, detector):
        """Test detection when both requests and limits are missing."""
        container = Mock()
        container.name = "test-container"
        container.resources = None

        issue = detector._check_missing_resources(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={"app": "test"}
        )

        assert issue is not None
        assert issue.severity == Severity.MEDIUM
        assert "Missing resource requests/limits" in issue.title
        assert issue.auto_fixable is True
        assert issue.platform == Platform.K8S
        assert issue.namespace == "default"
        assert issue.resource_name == "test-deployment"

    def test_check_missing_resources_requests_missing(self, detector):
        """Test detection when only requests are missing."""
        container = Mock()
        container.name = "test-container"
        container.resources = Mock()
        container.resources.requests = None
        container.resources.limits = {"cpu": "200m", "memory": "256Mi"}

        issue = detector._check_missing_resources(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={}
        )

        assert issue is not None
        assert "requests" in issue.title
        assert issue.severity == Severity.MEDIUM

    def test_check_missing_resources_limits_missing(self, detector):
        """Test detection when only limits are missing."""
        container = Mock()
        container.name = "test-container"
        container.resources = Mock()
        container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
        container.resources.limits = None

        issue = detector._check_missing_resources(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={}
        )

        assert issue is not None
        assert "limits" in issue.title

    def test_check_missing_resources_all_present(self, detector):
        """Test no issue when both requests and limits are present."""
        container = Mock()
        container.name = "test-container"
        container.resources = Mock()
        container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
        container.resources.limits = {"cpu": "200m", "memory": "256Mi"}

        issue = detector._check_missing_resources(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={}
        )

        assert issue is None

    def test_check_over_provisioned_cpu(self, detector):
        """Test detection of over-provisioned CPU."""
        container = Mock()
        container.name = "test-container"
        container.resources = Mock()
        container.resources.requests = {"cpu": "3", "memory": "1Gi"}
        container.resources.limits = {"cpu": "4", "memory": "2Gi"}

        issue = detector._check_over_provisioned(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={}
        )

        assert issue is not None
        assert issue.severity == Severity.LOW
        assert "Over-provisioned" in issue.title
        assert issue.auto_fixable is True
        assert "1500m" in issue.recommended_value["requests"]["cpu"]  # 50% of 3 cores

    def test_check_over_provisioned_memory(self, detector):
        """Test detection of over-provisioned memory."""
        container = Mock()
        container.name = "test-container"
        container.resources = Mock()
        container.resources.requests = {"cpu": "1", "memory": "8Gi"}  # 8Gi > 4Gi threshold
        container.resources.limits = {"cpu": "2", "memory": "16Gi"}

        issue = detector._check_over_provisioned(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={}
        )

        assert issue is not None
        assert issue.severity == Severity.LOW
        assert "Over-provisioned" in issue.title

    def test_check_over_provisioned_normal_resources(self, detector):
        """Test no issue for normal resource allocation."""
        container = Mock()
        container.name = "test-container"
        container.resources = Mock()
        container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
        container.resources.limits = {"cpu": "200m", "memory": "256Mi"}

        issue = detector._check_over_provisioned(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={}
        )

        assert issue is None

    def test_check_over_provisioned_no_requests(self, detector):
        """Test no issue when requests are missing."""
        container = Mock()
        container.name = "test-container"
        container.resources = Mock()
        container.resources.requests = None
        container.resources.limits = {"cpu": "4", "memory": "8Gi"}

        issue = detector._check_over_provisioned(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={}
        )

        assert issue is None

    @pytest.mark.asyncio
    async def test_check_deployments_with_issues(self, detector, mocker):
        """Test checking deployments with resource issues."""
        # Mock Kubernetes client
        mock_deployment = Mock()
        mock_deployment.metadata.name = "test-deployment"
        mock_deployment.metadata.namespace = "default"
        mock_deployment.metadata.labels = {"app": "test"}

        # Mock pod spec with missing resources
        mock_container = Mock()
        mock_container.name = "app"
        mock_container.resources = None

        mock_deployment.spec.template.spec.containers = [mock_container]

        mock_list_result = Mock()
        mock_list_result.items = [mock_deployment]

        detector._k8s_client = Mock()
        detector._k8s_client.list_deployment_for_all_namespaces.return_value = mock_list_result

        issues = await detector._check_deployments()

        assert len(issues) > 0
        assert issues[0].resource_type == "Deployment"
        assert issues[0].resource_name == "test-deployment"

    @pytest.mark.asyncio
    async def test_check_deployments_skip_system_namespace(self, detector):
        """Test skipping system namespace deployments."""
        mock_deployment = Mock()
        mock_deployment.metadata.name = "coredns"
        mock_deployment.metadata.namespace = "kube-system"
        mock_deployment.metadata.labels = {}

        mock_list_result = Mock()
        mock_list_result.items = [mock_deployment]

        detector._k8s_client = Mock()
        detector._k8s_client.list_deployment_for_all_namespaces.return_value = mock_list_result

        issues = await detector._check_deployments()

        assert len(issues) == 0  # Should skip kube-system

    def test_resource_to_dict(self, detector):
        """Test converting resources to dictionary."""
        resources = {"cpu": "100m", "memory": "128Mi"}
        result = detector._resource_to_dict(resources)

        assert result == {"cpu": "100m", "memory": "128Mi"}

    def test_resource_to_dict_none(self, detector):
        """Test converting None resources."""
        result = detector._resource_to_dict(None)
        assert result is None

    def test_recommended_values_for_missing_resources(self, detector):
        """Test recommended values are reasonable."""
        container = Mock()
        container.name = "test-container"
        container.resources = None

        issue = detector._check_missing_resources(
            name="test-deployment",
            namespace="default",
            resource_type="Deployment",
            container=container,
            labels={}
        )

        assert issue.recommended_value["requests"]["cpu"] == "100m"
        assert issue.recommended_value["requests"]["memory"] == "128Mi"
        assert issue.recommended_value["limits"]["cpu"] == "200m"
        assert issue.recommended_value["limits"]["memory"] == "256Mi"
