"""Test detection capabilities."""

import pytest
from kubernetes import client


@pytest.mark.e2e
class TestK8sDetection:
    """Test Kubernetes resource detection."""

    def test_detect_deployment_without_resources(self, k8s_client, test_namespace):
        """Test detection of deployments without resource limits."""
        deployment = k8s_client.read_namespaced_deployment(
            name="no-resources-app",
            namespace=test_namespace
        )

        # Verify the issue exists
        container = deployment.spec.template.spec.containers[0]
        assert container.resources is None or container.resources.limits is None, \
            "Deployment should be missing resource limits (this is intentional for testing)"

    def test_detect_excessive_replicas(self, k8s_client, test_namespace):
        """Test detection of excessive replica counts."""
        deployment = k8s_client.read_namespaced_deployment(
            name="excessive-replicas-app",
            namespace=test_namespace
        )

        # Verify the issue exists
        assert deployment.spec.replicas == 20, \
            "Deployment should have 20 replicas (intentional misconfiguration)"

    def test_detect_over_provisioned_resources(self, k8s_client, test_namespace):
        """Test detection of over-provisioned resources."""
        deployment = k8s_client.read_namespaced_deployment(
            name="over-provisioned-app",
            namespace=test_namespace
        )

        # Verify the issue exists
        container = deployment.spec.template.spec.containers[0]
        memory_request = container.resources.requests.get("memory")

        assert memory_request == "8Gi", \
            "Deployment should request 8Gi memory (intentional over-provisioning)"

    def test_detect_missing_probes(self, k8s_client, test_namespace):
        """Test detection of missing health check probes."""
        deployment = k8s_client.read_namespaced_deployment(
            name="no-probes-app",
            namespace=test_namespace
        )

        # Verify the issue exists
        container = deployment.spec.template.spec.containers[0]
        assert container.liveness_probe is None, \
            "Deployment should be missing liveness probe (intentional)"
        assert container.readiness_probe is None, \
            "Deployment should be missing readiness probe (intentional)"


@pytest.mark.e2e
@pytest.mark.skip(reason="Will be implemented with detection engine")
class TestDetectionEngine:
    """Test the full detection engine workflow."""

    async def test_detection_engine_finds_all_issues(self):
        """Test that detection engine finds all known issues."""
        # TODO: This will test the actual DetectionEngine
        # from src.core.detection_engine import DetectionEngine
        # engine = DetectionEngine(config)
        # issues = await engine.run_detection()
        # assert len(issues) >= 5  # At least 5 known issues
        pass

    async def test_issues_have_correct_severity(self):
        """Test that detected issues are assigned correct severity."""
        # TODO: Verify severity classification
        pass

    async def test_issues_have_remediation_plans(self):
        """Test that issues include remediation suggestions."""
        # TODO: Verify remediation plans are generated
        pass
