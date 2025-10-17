"""Detector for Kubernetes Pod resource configurations."""

from typing import List
import structlog

from src.detectors.base.detector import BaseDetector, Issue, Platform, Severity


logger = structlog.get_logger(__name__)


class PodResourceDetector(BaseDetector):
    """Detects Pods without resource limits/requests."""

    @property
    def platform(self) -> Platform:
        return Platform.K8S

    @property
    def resource_type(self) -> str:
        return "Pod"

    async def detect(self) -> List[Issue]:
        """Detect Pods missing resource configurations."""
        issues = []
        logger.info("Running Pod resource detection")

        # TODO: Implement K8s API calls
        # This will be implemented in the next step

        return issues
