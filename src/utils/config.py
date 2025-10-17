"""Configuration management."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class K8sConfig(BaseSettings):
    """Kubernetes configuration."""
    in_cluster: bool = False
    kubeconfig: Optional[str] = None
    contexts: List[Dict[str, Any]] = []


class AWSConfig(BaseSettings):
    """AWS configuration."""
    enabled: bool = True
    profile: Optional[str] = None
    regions: List[str] = ["us-east-1"]
    endpoint_url: Optional[str] = None
    resources: Dict[str, Any] = {}


class AzureConfig(BaseSettings):
    """Azure configuration."""
    enabled: bool = True
    subscriptions: List[Dict[str, Any]] = []
    resources: Dict[str, Any] = {}


class DetectionConfig(BaseSettings):
    """Detection engine configuration."""
    interval: int = 300
    parallel_workers: int = 5


class RemediationConfig(BaseSettings):
    """Remediation configuration."""
    enabled: bool = True
    auto_fix_severity: List[str] = ["low"]
    require_approval_severity: List[str] = ["medium", "high"]
    max_concurrent_fixes: int = 3


class GitHubConfig(BaseSettings):
    """GitHub configuration."""
    enabled: bool = True
    mode: str = "remote"  # "remote" or "local"
    local_repo_path: Optional[str] = None
    organization: Optional[str] = None
    repositories: Dict[str, Any] = {}


class NotificationsConfig(BaseSettings):
    """Notifications configuration."""
    teams: Dict[str, Any] = {}
    email: Dict[str, Any] = {}


class GrafanaConfig(BaseSettings):
    """Grafana configuration."""
    enabled: bool = False
    url: Optional[str] = None
    api_key: Optional[str] = None


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"


class MetricsConfig(BaseSettings):
    """Metrics configuration."""
    enabled: bool = True
    port: int = 9090
    path: str = "/metrics"


class Config(BaseSettings):
    """Main configuration."""
    environment: str = "production"
    k8s: K8sConfig = Field(default_factory=K8sConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    azure: AzureConfig = Field(default_factory=AzureConfig)
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    remediation: RemediationConfig = Field(default_factory=RemediationConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    grafana: GrafanaConfig = Field(default_factory=GrafanaConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)


def load_config(config_path: str) -> Config:
    """Load configuration from YAML file with environment variable substitution."""
    with open(config_path) as f:
        config_data = yaml.safe_load(f)

    # Substitute environment variables
    config_data = _substitute_env_vars(config_data)

    return Config(**config_data)


def _substitute_env_vars(data: Any) -> Any:
    """Recursively substitute ${VAR} with environment variables."""
    if isinstance(data, dict):
        return {k: _substitute_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_substitute_env_vars(item) for item in data]
    elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
        var_name = data[2:-1]
        return os.getenv(var_name, data)
    return data
