"""Scheduler for periodic detection runs."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import structlog

from src.core.remediation_orchestrator import RemediationOrchestrator


logger = structlog.get_logger(__name__)


class Scheduler:
    """Schedules periodic detection and remediation."""

    def __init__(self, config, detection_engine):
        self.config = config
        self.detection_engine = detection_engine
        self.remediation_orchestrator = RemediationOrchestrator(config)
        self.scheduler = AsyncIOScheduler()
        self.logger = structlog.get_logger(__name__)

    def start(self) -> None:
        """Start the scheduler."""
        interval = self.config.detection.interval

        self.scheduler.add_job(
            self._detection_job,
            trigger=IntervalTrigger(seconds=interval),
            id="detection_job",
            name="Run detection and remediation",
            replace_existing=True,
        )

        self.scheduler.start()
        self.logger.info(
            "Scheduler started",
            interval_seconds=interval
        )

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        self.logger.info("Scheduler stopped")

    async def _detection_job(self) -> None:
        """Execute detection and remediation job."""
        try:
            # Run detection
            issues = await self.detection_engine.run_detection()

            if not issues:
                self.logger.info("No issues detected")
                return

            # Process issues for remediation
            await self.remediation_orchestrator.process_issues(issues)

        except Exception as e:
            self.logger.error(
                "Detection job failed",
                error=str(e),
                exc_info=True
            )
