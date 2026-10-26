"""Data classes shared across the scanner."""

from dataclasses import dataclass, field

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEVERITIES = list(SEVERITY_ORDER)


def severity_from_cvss(score):
    """Map a CVSS v3 base score to a severity label."""
    if score is None:
        return "info"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    if score > 0:
        return "low"
    return "info"


@dataclass
class Device:
    host: str
    platform: str
    credential: str = ""
    name: str = ""
    site: str = ""

    @property
    def label(self):
        return self.name or self.host


@dataclass
class Facts:
    """What we learned about a device from its command output."""

    hostname: str = ""
    model: str = ""
    os_name: str = ""
    version: str = ""
    release: str = ""
    serial: str = ""
    raw: dict = field(default_factory=dict)  # command key -> output text (never exported)


@dataclass
class Finding:
    id: str
    title: str
    severity: str
    category: str  # "vulnerability" | "config" | "lifecycle"
    description: str = ""
    remediation: str = ""
    cvss: float | None = None
    cves: list = field(default_factory=list)
    kev: bool = False
    evidence: list = field(default_factory=list)
    references: list = field(default_factory=list)
    source: str = ""

    @property
    def priority(self):
        if self.kev or self.severity == "critical":
            return "P1"
        return {"high": "P2", "medium": "P3"}.get(self.severity, "P4")

    def sort_key(self):
        return (self.priority, SEVERITY_ORDER.get(self.severity, 9), -(self.cvss or 0), self.id)


@dataclass
class DeviceResult:
    device: Device
    status: str = "ok"  # "ok" | "failed" | "skipped"
    error: str = ""
    facts: Facts = field(default_factory=Facts)
    findings: list = field(default_factory=list)
    lifecycle: str = "unknown"
    notes: list = field(default_factory=list)
