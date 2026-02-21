from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Threat:
    agent: str
    description: str
    severity: Severity
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def __str__(self):
        return f"[{self.severity.value}] {self.agent}: {self.description}"
