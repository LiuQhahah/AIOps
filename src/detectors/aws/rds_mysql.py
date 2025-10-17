"""Detector for AWS RDS MySQL instances."""

from typing import List
import structlog

from src.detectors.base.detector import BaseDetector, Issue, Platform, Severity


logger = structlog.get_logger(__name__)


class RDSMySQLDetector(BaseDetector):
    """Detects RDS MySQL performance and configuration issues."""

    @property
    def platform(self) -> Platform:
        return Platform.AWS

    @property
    def resource_type(self) -> str:
        return "RDS"

    async def detect(self) -> List[Issue]:
        """Detect RDS MySQL issues."""
        issues = []
        logger.info("Running RDS MySQL detection")

        # TODO: Implement AWS RDS checks
        # - CPU utilization
        # - Connection count
        # - Storage space
        # - Instance class optimization

        return issues
