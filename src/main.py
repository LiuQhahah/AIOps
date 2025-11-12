"""Main entry point for the OpsAgent."""

import argparse
import asyncio
import signal
import sys
from pathlib import Path

import structlog

from src.utils.config import load_config
from src.utils.logger import setup_logging
from src.core.detection_engine import DetectionEngine
from src.core.scheduler import Scheduler
from src.api.server import create_app

logger = structlog.get_logger(__name__)


class OpsAgent:
    """Main OpsAgent orchestrator."""

    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        setup_logging(self.config.logging)
        self.logger = structlog.get_logger(__name__)

        self.detection_engine = DetectionEngine(self.config)
        self.scheduler = Scheduler(self.config, self.detection_engine)
        self.app = create_app(self.config)

        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the OpsAgent."""
        self.logger.info("Starting OpsAgent", environment=self.config.environment)

        # Register signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        # Start scheduler
        self.scheduler.start()
        self.logger.info("Detection scheduler started")

        # Start API server
        import uvicorn
        config_uvicorn = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=18080,
            log_config=None,  # Use structlog
        )
        server = uvicorn.Server(config_uvicorn)

        try:
            await server.serve()
        except asyncio.CancelledError:
            pass

    async def shutdown(self) -> None:
        """Gracefully shutdown the OpsAgent."""
        self.logger.info("Shutting down OpsAgent...")
        self.scheduler.shutdown()
        self._shutdown_event.set()


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Multi-Cloud OpsAgent")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file",
    )
    args = parser.parse_args()

    if not Path(args.config).exists():
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)

    agent = OpsAgent(args.config)

    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
