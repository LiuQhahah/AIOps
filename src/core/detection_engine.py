"""Core detection engine that orchestrates all platform detectors."""

from typing import List
import structlog

from src.detectors.base.detector import Issue


logger = structlog.get_logger(__name__)


class DetectionEngine:
    """Orchestrates detection across all platforms."""

    def __init__(self, config):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self.detectors = self._initialize_detectors()

    def _initialize_detectors(self):
        """Initialize all enabled detectors."""
        detectors = []

        # K8s detectors
        if self.config.k8s.contexts:
            from src.detectors.k8s.pod_resources import PodResourceDetector
            detectors.append(PodResourceDetector(self.config))
            self.logger.info("K8s detectors initialized")

        # AWS detectors
        if self.config.aws.enabled:
            if self.config.aws.resources.get("rds", {}).get("enabled"):
                from src.detectors.aws.rds_mysql import RDSMySQLDetector
                detectors.append(RDSMySQLDetector(self.config))

            if self.config.aws.resources.get("kinesis", {}).get("enabled"):
                from src.detectors.aws.kinesis_shards import KinesisShardDetector
                detectors.append(KinesisShardDetector(self.config))

            self.logger.info("AWS detectors initialized")

        # Azure detectors
        if self.config.azure.enabled:
            # Azure detectors will be added here
            self.logger.info("Azure detectors initialized")

        return detectors

    async def run_detection(self) -> List[Issue]:
        """Run all detectors and collect issues."""
        self.logger.info("Starting detection cycle")
        all_issues = []

        for detector in self.detectors:
            try:
                self.logger.debug(
                    "Running detector",
                    detector=detector.__class__.__name__
                )
                issues = await detector.detect()
                all_issues.extend(issues)
                self.logger.info(
                    "Detector completed",
                    detector=detector.__class__.__name__,
                    issues_found=len(issues)
                )
            except Exception as e:
                self.logger.error(
                    "Detector failed",
                    detector=detector.__class__.__name__,
                    error=str(e),
                    exc_info=True
                )

        self.logger.info(
            "Detection cycle completed",
            total_issues=len(all_issues)
        )
        return all_issues
