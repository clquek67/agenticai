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
    product: str = ""  # manual appliances: NVD "vendor:product" (several separated by ";")
    version: str = ""  # manual appliances: software/firmware version from the inventory

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
    # Servers: installed software such as PHP. Each item: name, version, build, sapi, path, ini.
    software: list = field(default_factory=list)
    packages: dict = field(default_factory=dict)  # Linux package name -> version
    fixed_cves: set = field(default_factory=set)  # CVEs the distro package changelogs say are fixed
    os_id: str = ""  # Linux os-release ID (ubuntu, rhel, rocky, ...)
    kernel: str = ""  # running Linux kernel (uname -r)
    pkg_records: list = field(default_factory=list)  # Linux: name, version, source, source_version
    build: str = ""  # Windows: 10.0.<build>.<UBR>
    install_type: str = ""  # Windows: "Server" or "Server Core"


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
    fix_group: str = ""  # the action that fixes it, e.g. "Update package php8.3"
    epss: float | None = None  # probability of exploitation in the next 30 days (FIRST EPSS)
    confidence: str = "confirmed"  # or "possible" when the match depends on things not checked

    @property
    def priority(self):
        epss = self.epss or 0
        if self.kev or self.severity == "critical" or epss >= 0.5:
            return "P1"
        if self.severity == "high" or epss >= 0.1:
            return "P2"
        return "P3" if self.severity == "medium" else "P4"

    def sort_key(self):
        return (self.priority, SEVERITY_ORDER.get(self.severity, 9), -(self.epss or 0), -(self.cvss or 0), self.id)


@dataclass
class DeviceResult:
    device: Device
    status: str = "ok"  # "ok" | "failed" | "skipped"
    error: str = ""
    facts: Facts = field(default_factory=Facts)
    findings: list = field(default_factory=list)
    lifecycle: str = "unknown"
    notes: list = field(default_factory=list)
