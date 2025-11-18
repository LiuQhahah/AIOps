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

        self.logger.info(
            "Initializing detectors",
            k8s_contexts=len(self.config.k8s.contexts) if self.config.k8s.contexts else 0,
            aws_enabled=self.config.aws.enabled,
            azure_enabled=self.config.azure.enabled
        )

        # K8s detectors
        # Initialize if running in-cluster OR if contexts are configured
        if self.config.k8s.in_cluster or self.config.k8s.contexts:
            try:
                from src.detectors.k8s.pod_resources import PodResourceDetector
                detectors.append(PodResourceDetector(self.config))
                self.logger.info("K8s detectors initialized", count=1)
            except Exception as e:
                self.logger.error("Failed to initialize K8s detectors", error=str(e), exc_info=True)

        # AWS detectors
        if self.config.aws.enabled:
            aws_detector_count = 0
            if self.config.aws.resources.get("rds", {}).get("enabled"):
                try:
                    from src.detectors.aws.rds_mysql import RDSMySQLDetector
                    detectors.append(RDSMySQLDetector(self.config))
                    aws_detector_count += 1
                except Exception as e:
                    self.logger.error("Failed to initialize RDS detector", error=str(e), exc_info=True)

            if self.config.aws.resources.get("kinesis", {}).get("enabled"):
                try:
                    from src.detectors.aws.kinesis_shards import KinesisShardDetector
                    detectors.append(KinesisShardDetector(self.config))
                    aws_detector_count += 1
                except Exception as e:
                    self.logger.error("Failed to initialize Kinesis detector", error=str(e), exc_info=True)

            self.logger.info("AWS detectors initialized", count=aws_detector_count)

        # Azure detectors
        if self.config.azure.enabled:
            # Azure detectors will be added here
            self.logger.info("Azure detectors initialized", count=0)

        self.logger.info("Detector initialization complete", total_detectors=len(detectors))
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
