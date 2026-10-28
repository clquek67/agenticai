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
        if adv.get("platform") != platform_name:
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


# --- server software (PHP, ...) -------------------------------------------------

_ON = ("1", "on", "true", "yes")


def is_distro_build(install, facts):
    """True for PHP shipped by the Linux distribution, which backports fixes without
    changing the upstream version (e.g. Ubuntu '8.1.2-1ubuntu2.19', RHEL /usr/bin/php)."""
    if install["build"] != install["version"]:
        return True
    return bool(facts.packages) and install["path"].startswith(("/usr/bin/", "/usr/sbin/"))


def _describe(install):
    return f"{install['path']}: PHP {install['build']} ({install['sapi']})"


def run_software_advisories(platform_name, facts, advisories):
    """One finding per advisory per server, listing every affected install as evidence."""
    findings = []
    for adv in advisories:
        if "software" not in adv or platform_name not in adv.get("platforms", []):
            continue
        affected_lines, notes = [], []
        for inst in facts.software:
            if inst["name"] != adv["software"] or not _version_affected(inst["version"], adv.get("affected", {})):
                continue
            if adv["id"] in facts.fixed_cves and is_distro_build(inst, facts):
                continue  # the distro package changelog lists this CVE as fixed (backport)
            affected_lines.append(_describe(inst) + " is in the affected range")
            if is_distro_build(inst, facts):
                notes.append(f"{inst['path']} is a distribution package and its changelog does not list "
                             f"{adv['id']}: install your distribution's security update.")
            for key, bad in adv.get("mitigation_ini", {}).items():
                value = inst["ini"].get(key)
                if value is not None and value.lower() in bad:
                    notes.append(f"{inst['path']}: {key} = {value} (interim mitigation not applied)")
        if any("mitigation not applied" in n for n in notes):
            notes.append("Settings were read from the CLI php.ini; PHP-FPM, Apache or IIS may use a different php.ini.")
        if affected_lines:
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
                    evidence=affected_lines + notes,
                    references=adv.get("references", []),
                    source="Local advisory rule",
                    fix_group=f"Upgrade {adv['software'].upper()}",
                )
            )
    return findings


def check_software_lifecycle(facts, software_lifecycle):
    findings = []
    for entry in software_lifecycle:
        for inst in facts.software:
            if inst["name"] != entry["software"]:
                continue
            if versions.compare(versions.train(inst["version"]), entry["supported_from"]) >= 0:
                continue
            distro = is_distro_build(inst, facts)
            findings.append(
                Finding(
                    id=f"EOL-{entry['software'].upper()}-{versions.train(inst['version'])}",
                    title=f"{entry['label']} {versions.train(inst['version'])} is end of life upstream",
                    severity="low" if distro else "high",
                    category="lifecycle",
                    description=entry["note"] + (
                        " This install is a distribution package: check that your distribution still "
                        "supports it." if distro else ""),
                    remediation=entry["remediation"],
                    evidence=[_describe(inst)],
                    references=entry.get("references", []),
                    source="Lifecycle data",
                )
            )
    return findings
