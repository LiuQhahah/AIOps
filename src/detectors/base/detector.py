"""Base detector class and Issue model."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class Severity(str, Enum):
    """Issue severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Platform(str, Enum):
    """Supported platforms."""
    K8S = "k8s"
    AWS = "aws"
    AZURE = "azure"


@dataclass
class Issue:
    """Represents a detected configuration issue."""

    # Required fields (no defaults)
    platform: Platform
    resource_type: str
    resource_name: str
    severity: Severity
    title: str
    description: str

    # Identification (with defaults)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detected_at: datetime = field(default_factory=datetime.utcnow)

    # Context
    namespace: Optional[str] = None
    region: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    # Remediation
    remediation_plan: Optional[Dict[str, Any]] = None
    auto_fixable: bool = False

    # Metadata
    current_value: Optional[Any] = None
    recommended_value: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "platform": self.platform.value,
            "resource_type": self.resource_type,
            "resource_name": self.resource_name,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "namespace": self.namespace,
            "region": self.region,
            "tags": self.tags,
            "auto_fixable": self.auto_fixable,
            "current_value": self.current_value,
            "recommended_value": self.recommended_value,
            "metadata": self.metadata,
        }


class BaseDetector(ABC):
    """Base class for all detectors."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    async def detect(self) -> List[Issue]:
        """Run detection and return list of issues found."""
        pass

    @property
    @abstractmethod
    def platform(self) -> Platform:
        """Return the platform this detector targets."""
        pass

    @property
    @abstractmethod
    def resource_type(self) -> str:
        """Return the resource type this detector checks."""
        pass
