"""Detector for AWS Kinesis stream shard configurations."""

from typing import List
import structlog

from src.detectors.base.detector import BaseDetector, Issue, Platform, Severity


logger = structlog.get_logger(__name__)


class KinesisShardDetector(BaseDetector):
    """Detects Kinesis shard over/under-provisioning."""

    @property
    def platform(self) -> Platform:
        return Platform.AWS

    @property
    def resource_type(self) -> str:
        return "Kinesis"

    async def detect(self) -> List[Issue]:
        """Detect Kinesis shard issues."""
        issues = []
        logger.info("Running Kinesis shard detection")

        # TODO: Implement Kinesis checks
        # - Shard count vs throughput
        # - Iterator age
        # - Write/Read provisioned throughput

        return issues
