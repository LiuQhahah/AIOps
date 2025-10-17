"""Orchestrates the remediation workflow."""

from typing import List
import structlog

from src.detectors.base.detector import Issue


logger = structlog.get_logger(__name__)


class RemediationOrchestrator:
    """Orchestrates the full remediation workflow."""

    def __init__(self, config):
        self.config = config
        self.logger = structlog.get_logger(__name__)

    async def process_issues(self, issues: List[Issue]) -> None:
        """Process detected issues and trigger remediation."""
        self.logger.info("Processing issues for remediation", count=len(issues))

        for issue in issues:
            try:
                await self._process_single_issue(issue)
            except Exception as e:
                self.logger.error(
                    "Failed to process issue",
                    issue_id=issue.id,
                    error=str(e),
                    exc_info=True
                )

    async def _process_single_issue(self, issue: Issue) -> None:
        """Process a single issue."""
        self.logger.info(
            "Processing issue",
            issue_id=issue.id,
            severity=issue.severity,
            resource=f"{issue.platform}/{issue.resource_type}/{issue.resource_name}"
        )

        # Check if auto-fix is allowed
        if issue.severity in self.config.remediation.auto_fix_severity:
            self.logger.info("Issue eligible for auto-fix", issue_id=issue.id)
            # TODO: Implement auto-fix logic
        else:
            self.logger.info(
                "Issue requires approval",
                issue_id=issue.id,
                severity=issue.severity
            )
            # TODO: Implement approval workflow
