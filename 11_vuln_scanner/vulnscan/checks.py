"""Offline checks driven by the JSON files in ``data/``.

* config rules      -> hardening findings from the running configuration
* local advisories  -> CVEs matched on version (+ optional config condition)
* lifecycle         -> end-of-sale / end-of-support findings from the model
"""

import json
import os
import re

from . import versions
from .models import Finding, severity_from_cvss

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Secrets that must never appear in evidence or reports.
_REDACT = [
    (re.compile(r"(\bcommunity\s+(?:read\s+|write\s+)?(?:simple\s+|cipher\s+)?)\S+", re.I), r"\1****"),
    (re.compile(r"(\b(?:password|secret|key)\s+(?:simple\s+|cipher\s+|hash\s+|\d\s+)?)\S+", re.I), r"\1****"),
]


def redact(line):
    for pattern, repl in _REDACT:
        line = pattern.sub(repl, line)
    return line


def load_json(name, data_dir=DATA_DIR):
    with open(os.path.join(data_dir, name), encoding="utf-8") as f:
        return json.load(f)


def _flags(rule):
    return re.MULTILINE | (re.IGNORECASE if rule.get("ignore_case") else 0)


# --- configuration hardening ---------------------------------------------------

def run_config_rules(platform_name, config, rules):
    """``present`` rules fire when the pattern matches; ``absent`` rules when it doesn't."""
    findings = []
    if not config:
        return findings
    for rule in rules:
        if rule["platform"] != platform_name:
            continue
        matches = [m.group(0).strip() for m in re.finditer(rule["pattern"], config, _flags(rule))]
        if rule["type"] == "present" and matches:
            evidence = list(dict.fromkeys(redact(m) for m in matches))[:5]
            if len(matches) > len(evidence):
                evidence.append(f"({len(matches)} matching lines in total)")
        elif rule["type"] == "absent" and not matches:
            evidence = ["Not found in the running configuration"]
        else:
            continue
        findings.append(
            Finding(
                id=rule["id"],
                title=rule["title"],
                severity=rule["severity"],
                category="config",
                description=rule.get("description", ""),
                remediation=rule.get("remediation", ""),
                evidence=evidence,
                references=rule.get("references", []),
                source="Config rule",
            )
        )
    return findings


# --- local advisory rules ------------------------------------------------------

def _version_affected(value, affected):
    if not value:
        return False
    if "version_regex" in affected and not re.search(affected["version_regex"], value):
        return False
    fixed_by_train = affected.get("fixed_by_train")
    if fixed_by_train:
        depth = affected.get("train_depth", 2)
        fixed = fixed_by_train.get(versions.train(value, depth))
        if fixed and versions.compare(value, fixed) >= 0:
            return False
        # A train with no listed fix is treated as affected: upgrade to a fixed train.
    if "fixed_in" in affected and versions.compare(value, affected["fixed_in"]) >= 0:
        return False
    if "introduced" in affected and versions.compare(value, affected["introduced"]) < 0:
        return False
    if "not_affected_from" in affected and versions.compare(value, affected["not_affected_from"]) >= 0:
        return False
    return True


def run_local_advisories(platform_name, facts, advisories):
    findings = []
    config = facts.raw.get("config", "")
    for adv in advisories:
        if adv["platform"] != platform_name:
            continue
        if adv.get("os") and adv["os"] != facts.os_name:
            continue
        if adv.get("model_regex") and not re.search(adv["model_regex"], facts.model or "", re.I):
            continue
        affected = adv.get("affected", {})
        value = getattr(facts, affected.get("field", "version"), "")
        if not _version_affected(value, affected):
            continue
        evidence = [f"{facts.os_name} {value} is in the affected range"]
        if adv.get("requires_config"):
            if not config:
                evidence.append("Running config not collected: exposure could not be confirmed")
            else:
                m = re.search(adv["requires_config"], config, re.MULTILINE)
                if not m:
                    continue  # vulnerable version, but the affected feature is not enabled
                evidence.append(f"Affected feature enabled: {redact(m.group(0).strip())}")
        findings.append(
            Finding(
                id=adv["id"],
                title=adv["title"],
                severity=adv.get("severity") or severity_from_cvss(adv.get("cvss")),
                category="vulnerability",
                description=adv.get("description", ""),
                remediation=adv.get("remediation", ""),
                cvss=adv.get("cvss"),
                cves=adv.get("cves", [adv["id"]]),
                evidence=evidence,
                references=adv.get("references", []),
                source="Local advisory rule",
            )
        )
    return findings


# --- hardware / software lifecycle --------------------------------------------

def check_lifecycle(facts, lifecycle):
    """Return (status, finding or None) for the device's model."""
    for entry in lifecycle:
        if facts.model and re.search(entry["model_regex"], facts.model, re.I):
            status = entry["status"]
            if status == "end_of_support":
                return status, Finding(
                    id="EOL-HW",
                    title=f"{facts.model} is past vendor end of support",
                    severity="high",
                    category="lifecycle",
                    description="The vendor no longer releases security fixes for this model, so new "
                    "vulnerabilities on it will stay unpatched.",
                    remediation="Plan a hardware replacement. Until then, restrict management access "
                    "to a dedicated management network.",
                    evidence=[entry.get("note", "")],
                    references=[entry["source"]] if entry.get("source") else [],
                    source="Lifecycle data",
                )
            if status == "end_of_sale":
                return status, Finding(
                    id="EOS-HW",
                    title=f"{facts.model} is end of sale; support is ending",
                    severity="low",
                    category="lifecycle",
                    description="The model is no longer sold. Security fixes continue only until the "
                    "vendor's last date of support.",
                    remediation="Add the device to the hardware refresh plan.",
                    evidence=[entry.get("note", "")],
                    references=[entry["source"]] if entry.get("source") else [],
                    source="Lifecycle data",
                )
            return status, None
    return "unknown", None
