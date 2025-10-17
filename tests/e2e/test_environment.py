"""Test that the E2E environment is set up correctly."""

import pytest
from kubernetes import client, config


@pytest.mark.e2e
class TestEnvironmentSetup:
    """Verify the Kind cluster and test fixtures are properly configured."""

    def test_cluster_is_accessible(self, k8s_client):
        """Test that we can connect to the Kind cluster."""
        nodes = client.CoreV1Api().list_node()
        assert len(nodes.items) >= 2, "Should have at least 2 nodes (control-plane + worker)"

    def test_test_namespace_exists(self, k8s_core_client, test_namespace):
        """Test that the test-app namespace exists."""
        namespaces = k8s_core_client.list_namespace()
        namespace_names = [ns.metadata.name for ns in namespaces.items]

        assert test_namespace in namespace_names, f"Namespace '{test_namespace}' should exist"

    def test_ops_agent_namespace_exists(self, k8s_core_client):
        """Test that the ops-agent namespace exists."""
        namespaces = k8s_core_client.list_namespace()
        namespace_names = [ns.metadata.name for ns in namespaces.items]

        assert "ops-agent" in namespace_names, "Namespace 'ops-agent' should exist"

    def test_test_deployments_exist(self, k8s_client, test_namespace):
        """Test that test fixtures are deployed."""
        deployments = k8s_client.list_namespaced_deployment(namespace=test_namespace)

        deployment_names = [d.metadata.name for d in deployments.items]

        # Check for expected test deployments
        expected = [
            "no-resources-app",
            "excessive-replicas-app",
            "over-provisioned-app",
        ]

        for expected_deployment in expected:
            assert expected_deployment in deployment_names, \
                f"Deployment '{expected_deployment}' should be deployed"

    def test_cluster_has_correct_labels(self):
        """Test that nodes have expected labels."""
        core_api = client.CoreV1Api()
        nodes = core_api.list_node()

        control_plane_found = False
        for node in nodes.items:
            labels = node.metadata.labels
            if "node-role.kubernetes.io/control-plane" in labels:
                control_plane_found = True
                assert labels.get("environment") == "test"
                assert labels.get("ops-agent") == "enabled"

        assert control_plane_found, "Should have a control-plane node with correct labels"
