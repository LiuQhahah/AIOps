"""Detector for Kubernetes Pod resource configurations."""

from typing import List, Optional, Dict, Any
import structlog
from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException

from src.detectors.base.detector import BaseDetector, Issue, Platform, Severity


logger = structlog.get_logger(__name__)


class PodResourceDetector(BaseDetector):
    """Detects Pods without resource limits/requests and over-provisioned Pods."""

    # Resource thresholds for detection
    OVER_PROVISIONED_CPU_THRESHOLD = 2.0  # CPU cores
    OVER_PROVISIONED_MEMORY_THRESHOLD = 4 * 1024 * 1024 * 1024  # 4Gi in bytes

    # Recommended default resources
    DEFAULT_CPU_REQUEST = "100m"
    DEFAULT_CPU_LIMIT = "200m"
    DEFAULT_MEMORY_REQUEST = "128Mi"
    DEFAULT_MEMORY_LIMIT = "256Mi"

    def __init__(self, config):
        super().__init__(config)
        self._k8s_client: Optional[client.AppsV1Api] = None
        self._core_v1_client: Optional[client.CoreV1Api] = None

    def _initialize_k8s_client(self) -> None:
        """Initialize Kubernetes client."""
        if self._k8s_client is not None:
            return

        try:
            if self.config.k8s.in_cluster:
                k8s_config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            else:
                k8s_config.load_kube_config()
                logger.info("Loaded kubeconfig from local environment")

            self._k8s_client = client.AppsV1Api()
            self._core_v1_client = client.CoreV1Api()
        except Exception as e:
            logger.error("Failed to initialize Kubernetes client", error=str(e))
            raise

    @property
    def platform(self) -> Platform:
        return Platform.K8S

    @property
    def resource_type(self) -> str:
        return "Pod"

    async def detect(self) -> List[Issue]:
        """Detect Pods missing resource configurations and over-provisioned Pods."""
        issues = []
        logger.info("Running Pod resource detection")

        try:
            self._initialize_k8s_client()

            # Check all Deployments
            deployment_issues = await self._check_deployments()
            issues.extend(deployment_issues)

            # Check all StatefulSets
            statefulset_issues = await self._check_statefulsets()
            issues.extend(statefulset_issues)

            # Check all DaemonSets
            daemonset_issues = await self._check_daemonsets()
            issues.extend(daemonset_issues)

            logger.info(
                "Pod resource detection completed",
                total_issues=len(issues)
            )
        except Exception as e:
            logger.error(
                "Pod resource detection failed",
                error=str(e),
                exc_info=True
            )

        return issues

    async def _check_deployments(self) -> List[Issue]:
        """Check Deployments for resource issues."""
        issues = []

        try:
            deployments = self._k8s_client.list_deployment_for_all_namespaces()
            logger.debug(f"Found {len(deployments.items)} deployments to check")

            for deployment in deployments.items:
                if self._should_skip_namespace(deployment.metadata.namespace):
                    continue

                deployment_issues = self._check_pod_template(
                    name=deployment.metadata.name,
                    namespace=deployment.metadata.namespace,
                    resource_type="Deployment",
                    pod_spec=deployment.spec.template.spec,
                    labels=deployment.metadata.labels or {}
                )
                issues.extend(deployment_issues)

        except ApiException as e:
            logger.error("Failed to list deployments", error=str(e))

        return issues

    async def _check_statefulsets(self) -> List[Issue]:
        """Check StatefulSets for resource issues."""
        issues = []

        try:
            statefulsets = self._k8s_client.list_stateful_set_for_all_namespaces()
            logger.debug(f"Found {len(statefulsets.items)} statefulsets to check")

            for statefulset in statefulsets.items:
                if self._should_skip_namespace(statefulset.metadata.namespace):
                    continue

                statefulset_issues = self._check_pod_template(
                    name=statefulset.metadata.name,
                    namespace=statefulset.metadata.namespace,
                    resource_type="StatefulSet",
                    pod_spec=statefulset.spec.template.spec,
                    labels=statefulset.metadata.labels or {}
                )
                issues.extend(statefulset_issues)

        except ApiException as e:
            logger.error("Failed to list statefulsets", error=str(e))

        return issues

    async def _check_daemonsets(self) -> List[Issue]:
        """Check DaemonSets for resource issues."""
        issues = []

        try:
            daemonsets = self._k8s_client.list_daemon_set_for_all_namespaces()
            logger.debug(f"Found {len(daemonsets.items)} daemonsets to check")

            for daemonset in daemonsets.items:
                if self._should_skip_namespace(daemonset.metadata.namespace):
                    continue

                daemonset_issues = self._check_pod_template(
                    name=daemonset.metadata.name,
                    namespace=daemonset.metadata.namespace,
                    resource_type="DaemonSet",
                    pod_spec=daemonset.spec.template.spec,
                    labels=daemonset.metadata.labels or {}
                )
                issues.extend(daemonset_issues)

        except ApiException as e:
            logger.error("Failed to list daemonsets", error=str(e))

        return issues

    def _should_skip_namespace(self, namespace: str) -> bool:
        """Check if namespace should be skipped (system namespaces)."""
        skip_namespaces = {'kube-system', 'kube-public', 'kube-node-lease', 'local-path-storage'}
        return namespace in skip_namespaces

    def _check_pod_template(
        self,
        name: str,
        namespace: str,
        resource_type: str,
        pod_spec: Any,
        labels: Dict[str, str]
    ) -> List[Issue]:
        """Check pod template for resource issues."""
        issues = []

        if not pod_spec or not pod_spec.containers:
            return issues

        for container in pod_spec.containers:
            # Check for missing resources
            missing_issue = self._check_missing_resources(
                name, namespace, resource_type, container, labels
            )
            if missing_issue:
                issues.append(missing_issue)

            # Check for over-provisioned resources
            over_provisioned_issue = self._check_over_provisioned(
                name, namespace, resource_type, container, labels
            )
            if over_provisioned_issue:
                issues.append(over_provisioned_issue)

        return issues

    def _check_missing_resources(
        self,
        name: str,
        namespace: str,
        resource_type: str,
        container: Any,
        labels: Dict[str, str]
    ) -> Optional[Issue]:
        """Check if container is missing resource limits/requests."""
        resources = container.resources

        missing_limits = not resources or not resources.limits
        missing_requests = not resources or not resources.requests

        if not missing_limits and not missing_requests:
            return None

        # Determine what's missing
        missing_items = []
        if missing_requests:
            missing_items.append("requests")
        if missing_limits:
            missing_items.append("limits")

        return Issue(
            platform=Platform.K8S,
            resource_type=resource_type,
            resource_name=name,
            namespace=namespace,
            severity=Severity.MEDIUM,
            title=f"Missing resource {'/'.join(missing_items)}",
            description=(
                f"Container '{container.name}' in {resource_type} '{name}' "
                f"is missing resource {'/'.join(missing_items)}. "
                f"This can lead to unpredictable scheduling and potential resource contention."
            ),
            auto_fixable=True,
            current_value={
                "container": container.name,
                "requests": self._resource_to_dict(resources.requests) if resources and resources.requests else None,
                "limits": self._resource_to_dict(resources.limits) if resources and resources.limits else None,
            },
            recommended_value={
                "requests": {
                    "cpu": self.DEFAULT_CPU_REQUEST,
                    "memory": self.DEFAULT_MEMORY_REQUEST,
                },
                "limits": {
                    "cpu": self.DEFAULT_CPU_LIMIT,
                    "memory": self.DEFAULT_MEMORY_LIMIT,
                },
            },
            tags=labels,
            metadata={
                "container": container.name,
                "missing_requests": missing_requests,
                "missing_limits": missing_limits,
            }
        )

    def _check_over_provisioned(
        self,
        name: str,
        namespace: str,
        resource_type: str,
        container: Any,
        labels: Dict[str, str]
    ) -> Optional[Issue]:
        """Check if container is over-provisioned."""
        resources = container.resources

        if not resources or not resources.requests:
            return None

        cpu_request = resources.requests.get('cpu')
        memory_request = resources.requests.get('memory')

        # Parse CPU (convert to cores)
        cpu_cores = self._parse_cpu(cpu_request) if cpu_request else 0
        # Parse memory (convert to bytes)
        memory_bytes = self._parse_memory(memory_request) if memory_request else 0

        is_over_provisioned = (
            cpu_cores > self.OVER_PROVISIONED_CPU_THRESHOLD or
            memory_bytes > self.OVER_PROVISIONED_MEMORY_THRESHOLD
        )

        if not is_over_provisioned:
            return None

        # Calculate recommended values (50% of current)
        recommended_cpu = f"{int(cpu_cores * 500)}m"  # 50% in millicores
        recommended_memory = f"{int(memory_bytes / (1024 * 1024) * 0.5)}Mi"  # 50% in MiB

        return Issue(
            platform=Platform.K8S,
            resource_type=resource_type,
            resource_name=name,
            namespace=namespace,
            severity=Severity.LOW,
            title="Over-provisioned resources",
            description=(
                f"Container '{container.name}' in {resource_type} '{name}' "
                f"has excessive resource requests (CPU: {cpu_request}, Memory: {memory_request}). "
                f"Consider reducing to optimize cluster utilization."
            ),
            auto_fixable=True,
            current_value={
                "container": container.name,
                "requests": {
                    "cpu": cpu_request,
                    "memory": memory_request,
                },
                "limits": self._resource_to_dict(resources.limits) if resources.limits else None,
            },
            recommended_value={
                "requests": {
                    "cpu": recommended_cpu,
                    "memory": recommended_memory,
                },
                "limits": {
                    "cpu": f"{int(cpu_cores * 1000)}m",  # 2x of recommended request
                    "memory": f"{int(memory_bytes / (1024 * 1024))}Mi",
                },
            },
            tags=labels,
            metadata={
                "container": container.name,
                "cpu_cores": cpu_cores,
                "memory_bytes": memory_bytes,
            }
        )

    def _resource_to_dict(self, resources: Optional[Dict]) -> Optional[Dict[str, str]]:
        """Convert resource dict to simple dict."""
        if not resources:
            return None
        return {k: str(v) for k, v in resources.items()}

    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to cores (float)."""
        if not cpu_str:
            return 0.0

        cpu_str = str(cpu_str).strip()

        # Handle millicores (e.g., "100m")
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000.0

        # Handle cores (e.g., "1", "0.5")
        return float(cpu_str)

    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory string to bytes (int)."""
        if not memory_str:
            return 0

        memory_str = str(memory_str).strip()

        # Define multipliers
        multipliers = {
            'Ki': 1024,
            'Mi': 1024 ** 2,
            'Gi': 1024 ** 3,
            'Ti': 1024 ** 4,
            'K': 1000,
            'M': 1000 ** 2,
            'G': 1000 ** 3,
            'T': 1000 ** 4,
        }

        # Try to match suffix
        for suffix, multiplier in multipliers.items():
            if memory_str.endswith(suffix):
                value = float(memory_str[:-len(suffix)])
                return int(value * multiplier)

        # No suffix, assume bytes
        return int(float(memory_str))
