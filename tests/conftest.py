"""Pytest configuration and fixtures."""

import pytest
from kubernetes import client, config


@pytest.fixture(scope="session")
def k8s_client():
    """Load Kubernetes configuration and return API client."""
    try:
        config.load_kube_config(context="kind-ops-agent-test")
    except Exception:
        # Fallback to default context
        config.load_kube_config()

    return client.AppsV1Api()


@pytest.fixture(scope="session")
def k8s_core_client():
    """Return Core V1 API client."""
    try:
        config.load_kube_config(context="kind-ops-agent-test")
    except Exception:
        config.load_kube_config()

    return client.CoreV1Api()


@pytest.fixture
def test_namespace():
    """Return test namespace name."""
    return "test-app"


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
