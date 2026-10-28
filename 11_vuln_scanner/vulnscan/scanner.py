"""Runs a scan: collect -> parse -> check -> enrich, one device per worker thread."""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from . import checks
from .collectors import CollectionError
from .inventory import in_scope
from .models import SEVERITIES, DeviceResult
from .platforms import get_platform

log = logging.getLogger("vulnscan")


class Scanner:
    def __init__(self, collector, kev, cisco_api=None, allowlist=None, workers=5, data_dir=checks.DATA_DIR):
        self.collector = collector
        self.kev = kev
        self.cisco_api = cisco_api
        self.allowlist = allowlist
        self.workers = workers
        self.config_rules = checks.load_json("config_rules.json", data_dir)
        self.advisories = checks.load_json("advisories.json", data_dir)
        self.lifecycle = checks.load_json("lifecycle.json", data_dir)
        self.software_lifecycle = checks.load_json("software_lifecycle.json", data_dir)

    def scan(self, devices):
        started = datetime.now(timezone.utc)
        with ThreadPoolExecutor(max_workers=max(1, self.workers)) as pool:
            results = list(pool.map(self.scan_device, devices))
        return ScanResult(results, started, datetime.now(timezone.utc), self)

    def scan_device(self, device):
        result = DeviceResult(device=device)
        if not in_scope(device.host, self.allowlist):
            result.status, result.error = "skipped", "outside the scan allowlist"
            return result
        platform = get_platform(device.platform)
        try:
            outputs = self.collector.collect(device, platform)
        except CollectionError as exc:
            result.status, result.error = "failed", str(exc)
            log.warning("%s: %s", device.label, exc)
            return result

        facts = platform.parse(outputs)
        facts.raw = outputs
        result.facts = facts
        if not facts.version:
            result.notes.append("Software version not recognised in the output; CVE matching skipped.")
        if platform.name in ("linux", "windows") and not facts.software:
            result.notes.append("No PHP installation found.")
        backported = sorted(facts.fixed_cves & {a["id"] for a in self.advisories if "software" in a})
        if backported:
            result.notes.append("Distribution package changelogs list fixes for " + ", ".join(backported) + ".")
        if "config" in platform.commands and "config" not in outputs:
            result.notes.append("Running configuration not collected; config checks skipped.")

        findings = []
        result.lifecycle, eol = checks.check_lifecycle(facts, self.lifecycle)
        if eol:
            findings.append(eol)
        findings += checks.run_local_advisories(platform.name, facts, self.advisories)
        findings += checks.run_software_advisories(platform.name, facts, self.advisories)
        findings += checks.check_software_lifecycle(facts, self.software_lifecycle)
        if self.cisco_api and platform.name.startswith("cisco"):
            try:
                findings += self.cisco_api.findings(facts)
            except Exception as exc:  # network/API problems must not stop the scan
                result.notes.append(f"Cisco openVuln lookup failed: {exc}")
        findings += checks.run_config_rules(platform.name, outputs.get("config", ""), self.config_rules)

        result.findings = _dedupe(findings)
        for f in result.findings:
            f.kev = any(c in self.kev for c in f.cves)
        result.findings.sort(key=lambda f: f.sort_key())
        facts.raw = {}  # drop full configs as soon as checks are done
        log.info("%s: %s %s, %d findings", device.label, facts.model, facts.version, len(result.findings))
        return result


def _dedupe(findings):
    """Keep one finding per ID; the first one wins (local rules know about config exposure)."""
    seen = {}
    for f in findings:
        if f.id in seen:
            seen[f.id].references = list(dict.fromkeys(seen[f.id].references + f.references))
        else:
            seen[f.id] = f
    return list(seen.values())


class ScanResult:
    def __init__(self, results, started, finished, scanner):
        self.results = results
        self.started = started
        self.finished = finished
        self.kev_source = scanner.kev.source
        self.cisco_api_used = scanner.cisco_api is not None
        self.rule_counts = {
            "config": len(scanner.config_rules),
            "advisories": len(scanner.advisories),
            "lifecycle": len(scanner.lifecycle),
        }

    @property
    def scanned(self):
        return [r for r in self.results if r.status == "ok"]

    @property
    def not_scanned(self):
        return [r for r in self.results if r.status != "ok"]

    def all_findings(self):
        return [(r, f) for r in self.scanned for f in r.findings]

    def severity_counts(self):
        counts = dict.fromkeys(SEVERITIES, 0)
        for _, f in self.all_findings():
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def kev_count(self):
        return sum(1 for _, f in self.all_findings() if f.kev)

    def risk_score(self):
        """0-100. Weighted findings per scanned device, squashed so one bad device can't hide."""
        if not self.scanned:
            return 0
        weights = {"critical": 10, "high": 4, "medium": 1.5, "low": 0.3, "info": 0}
        points = sum(weights.get(f.severity, 0) + (10 if f.kev else 0) for _, f in self.all_findings())
        per_device = points / len(self.scanned)
        return round(100 * per_device / (per_device + 10))

    def grouped_issues(self):
        """Findings grouped by ID across devices, worst first: the 'top risks' list."""
        groups = {}
        for r, f in self.all_findings():
            g = groups.setdefault((f.id, f.title), {"finding": f, "devices": []})
            g["devices"].append(r.device.label)
            g["finding"].kev = g["finding"].kev or f.kev
        return sorted(groups.values(), key=lambda g: (g["finding"].sort_key(), -len(g["devices"])))


def default_report_dir(base="reports"):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(base, f"scan-{stamp}")
