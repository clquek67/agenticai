"""Use a downloaded feed folder on the offline scanner (``scan.py --feeds <folder>``).

Matches each scanned device against the local copies of OSV (Linux packages), Microsoft
(Windows builds), NVD (network devices, PHP), Cisco openVuln, and enriches every finding
with CISA KEV and EPSS. Nothing here touches the network.
"""

import gzip
import json
import os
import re
from datetime import datetime, timezone

from . import versions
from .feeds import advisory_finding
from .feedsync import sha256
from .models import Finding
from .vercmp import dotted_compare, dpkg_compare, rpm_compare

WINDOWS_BUILDS = {9200: "Windows Server 2012", 9600: "Windows Server 2012 R2", 14393: "Windows Server 2016",
                  17763: "Windows Server 2019", 20348: "Windows Server 2022", 26100: "Windows Server 2025"}
DISTRO_IDS = {"ubuntu": "ubuntu", "debian": "debian", "rhel": "rhel", "rocky": "rocky", "almalinux": "alma"}


class FeedError(Exception):
    pass


def distro_key(facts):
    """'ubuntu:24.04', 'debian:12', 'rhel:9', 'rocky:9', 'alma:9' or '' if not covered."""
    distro = DISTRO_IDS.get(facts.os_id)
    if not distro or not facts.version:
        return ""
    release = facts.version if distro == "ubuntu" else facts.version.split(".")[0]
    return f"{distro}:{release}"


def windows_product(facts):
    m = re.match(r"10\.0\.(\d+)\.\d+", facts.build or "")
    return WINDOWS_BUILDS.get(int(m.group(1))) if m else None


def feed_request(results):
    """What the sync machine must download for these scan results. No hosts or addresses."""
    req = {"distros": set(), "windows_products": set(), "cisco_versions": set(), "nvd_products": set()}
    for r in results:
        f = r.facts
        if r.device.platform == "linux" and distro_key(f):
            req["distros"].add(distro_key(f))
        elif r.device.platform == "windows" and windows_product(f):
            req["windows_products"].add(windows_product(f))
        elif r.device.platform.startswith("cisco") and f.version and f.os_name in ("IOS", "IOS XE", "ASA"):
            req["cisco_versions"].add(f"{f.os_name}|{f.version}")
        elif r.device.platform == "manual":
            for vp in r.device.product.split(";"):
                if ":" in vp:
                    req["nvd_products"].add(vp.strip().lower())
    return {k: sorted(v) for k, v in req.items()}


class FeedStore:
    def __init__(self, path, verify=True, max_age_days=7):
        self.path = path
        manifest = os.path.join(path, "manifest.json")
        if not os.path.exists(manifest):
            raise FeedError(f"{manifest} not found: run 'scan.py --sync-feeds' on the internet machine first")
        with open(manifest, encoding="utf-8") as f:
            self.manifest = json.load(f)
        self.warnings = []
        self._cache = {}
        now = datetime.now(timezone.utc)
        for name, entry in sorted(self.manifest.get("feeds", {}).items()):
            if not entry.get("file"):
                self.warnings.append(f"Feed '{name}' has never downloaded successfully: {entry.get('error', '')}")
                continue
            fpath = os.path.join(path, entry["file"])
            if not os.path.exists(fpath):
                raise FeedError(f"{fpath} is listed in the manifest but missing")
            if verify and sha256(fpath) != entry["sha256"]:
                raise FeedError(f"{fpath} does not match its checksum: the copy is incomplete or was changed")
            if entry.get("status") == "error":
                self.warnings.append(f"Feed '{name}' failed at the last sync ({entry.get('error', '')}); "
                                     f"using the copy from {entry.get('updated', '?')}")
            if entry.get("updated"):
                age = (now - datetime.fromisoformat(entry["updated"])).days
                if age > max_age_days:
                    self.warnings.append(f"Feed '{name}' is {age} days old")

    # --- loading ---------------------------------------------------------------

    def _file(self, name):
        entry = self.manifest.get("feeds", {}).get(name)
        return os.path.join(self.path, entry["file"]) if entry and entry.get("file") else None

    def _load(self, name):
        if name not in self._cache:
            path = self._file(name)
            if not path:
                self._cache[name] = None
            elif path.endswith(".gz"):
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    self._cache[name] = json.load(f)
            else:
                with open(path, encoding="utf-8") as f:
                    self._cache[name] = json.load(f)
        return self._cache[name]

    def has(self, name):
        return self._file(name) is not None

    def feed_dates(self):
        return {n: e.get("updated", "never") for n, e in sorted(self.manifest.get("feeds", {}).items())}

    @property
    def kev(self):
        data = self._load("kev")
        return set(data["cves"]) if data else set()

    @property
    def epss(self):
        return self._load("epss") or {}

    def nvd_index(self):
        if "_nvd_index" not in self._cache:
            index = {}
            for cve_id, entry in ((self._load("nvd") or {}).get("cves") or {}).items():
                for vp in {(m[0], m[1]) for m in entry["matches"]}:
                    index.setdefault(vp, []).append((cve_id, entry))
            self._cache["_nvd_index"] = index
        return self._cache["_nvd_index"]

    def msrc_entries(self, product):
        out = []
        for doc in ((self._load("msrc") or {}).get("docs") or {}).values():
            out += doc.get(product, [])
        return out

    def cisco_advisories(self, os_name, version):
        data = self._load("cisco") or {}
        return data.get(f"{os_name}|{version}")

    # --- matching --------------------------------------------------------------

    def linux_findings(self, facts, include_unfixed=False):
        """CVEs in installed packages, using the distribution's own fixed versions (OSV).

        CVEs the distribution has not fixed yet are summarised in a note rather than listed
        (there is no update to install), unless they are actively exploited or
        ``include_unfixed`` is set."""
        key = distro_key(facts)
        if not key:
            return [], [f"Linux distribution '{facts.os_id}' is not covered by the OSV feeds."]
        distro = key.split(":")[0]
        data = self._load(f"osv-{distro}")
        if not data:
            return [], [f"No OSV feed for {distro}: add it to the sync (feed-request.json)."]
        index = data["releases"].get(key)
        if index is None:
            return [], [f"The OSV feed has no data for {key}: add it to the sync (feed-request.json)."]
        records = data["records"]
        compare = dpkg_compare if distro in ("ubuntu", "debian") else rpm_compare
        best = {}
        for name, version in _package_candidates(facts, distro):
            for osv_id, introduced, fixed, last_affected in index.get(name, []):
                if compare is rpm_compare and not _same_stream(version, fixed or last_affected or introduced):
                    continue
                if introduced not in ("0", "") and compare(version, introduced) < 0:
                    continue
                if fixed and compare(version, fixed) >= 0:
                    continue
                if last_affected and compare(version, last_affected) > 0:
                    continue
                cves, sev, score, summary = records[osv_id]
                for cve in cves:
                    prev = best.get(cve)  # one finding per CVE: prefer an entry with a fix, then the newest fix
                    if prev and not (fixed and (prev[3] is None or compare(fixed, prev[3]) > 0)):
                        continue
                    best[cve] = (osv_id, name, version, fixed, [cve], sev, score, summary)
        findings, unfixed = [], {}
        kev = self.kev
        label = {"ubuntu": "Ubuntu", "debian": "Debian", "rhel": "Red Hat", "rocky": "Rocky Linux", "alma": "AlmaLinux"}[distro]
        for cve, (osv_id, name, version, fixed, cves, sev, score, summary) in best.items():
            if not fixed and not include_unfixed and cve not in kev:
                unfixed[name] = unfixed.get(name, 0) + 1
                continue
            findings.append(Finding(
                id=cve, title=summary or f"Vulnerability in {name}", severity=sev, category="vulnerability",
                remediation=f"Update {name} to {fixed} or later." if fixed else
                f"No {label} fix released yet for {name}; apply vendor mitigations.",
                cvss=score, cves=cves,
                evidence=[f"{name} {version} installed" + (f"; fixed in {fixed}" if fixed else "; no fix yet")],
                references=[f"https://osv.dev/vulnerability/{osv_id}"],
                source=f"OSV.dev ({label})", fix_group=f"Update package {name}" if fixed else f"No fix yet: {name}",
            ))
        notes = []
        if unfixed:
            top = ", ".join(f"{n} ({c})" for n, c in sorted(unfixed.items(), key=lambda x: -x[1])[:6])
            notes.append(f"{sum(unfixed.values())} high/critical CVEs have no {label} fix yet and are not listed "
                         f"(no update to install): {top}. Use --include-unfixed to list them.")
        return findings, notes

    def windows_findings(self, facts):
        """CVEs fixed by Windows cumulative updates newer than the server's build (Microsoft MSRC)."""
        if not self.has("msrc"):
            return [], ["No Microsoft (MSRC) feed: Windows CVEs not checked."]
        product = windows_product(facts)
        if not product:
            return [], [f"Windows build '{facts.build}' not recognised as a supported Windows Server version."]
        if facts.install_type == "Server Core":
            product += " (Server Core installation)"
        best = {}
        for cve, fixed_build, kb, sev, score, title in self.msrc_entries(product):
            if dotted_compare(facts.build, fixed_build) >= 0:
                continue
            prev = best.get(cve)
            if prev is None or dotted_compare(fixed_build, prev[0]) < 0:
                best[cve] = (fixed_build, kb, sev, score, title)
        findings = []
        for cve, (fixed_build, kb, sev, score, title) in best.items():
            findings.append(Finding(
                id=cve, title=title or "Windows vulnerability", severity=sev, category="vulnerability",
                remediation=f"Install KB{kb} (build {fixed_build}) or a later cumulative update.",
                cvss=score, cves=[cve],
                evidence=[f"{product} build {facts.build}; fixed in build {fixed_build}"],
                references=[f"https://msrc.microsoft.com/update-guide/vulnerability/{cve}"],
                source="Microsoft MSRC", fix_group="Install the latest Windows cumulative update",
            ))
        return findings, []

    def nvd_findings(self, product_versions, fix_group):
        """``product_versions``: [(vendor, product, [version spellings])]. Matches NVD CPE data."""
        index = self.nvd_index()
        findings = {}
        for vendor, product, spellings in product_versions:
            spellings = [s.lower() for s in spellings if s]
            if not spellings:
                continue
            for cve_id, entry in index.get((vendor, product), []):
                for v, p, ver, si, se, ei, ee, and_cfg in entry["matches"]:
                    if (v, p) != (vendor, product) or not _nvd_match(spellings, ver, si, se, ei, ee):
                        continue
                    findings[cve_id] = Finding(
                        id=cve_id, title=entry["desc"][:140] or cve_id, severity=entry["sev"],
                        category="vulnerability", cvss=entry["cvss"], cves=[cve_id],
                        remediation="Upgrade to a release the vendor lists as fixed for this CVE.",
                        evidence=[f"{product} {spellings[0]} matches NVD's affected range"]
                        + (["Only affected in some hardware/software combinations: verify"] if and_cfg else []),
                        references=[f"https://nvd.nist.gov/vuln/detail/{cve_id}"],
                        source="NVD", fix_group=fix_group, confidence="possible" if and_cfg else "confirmed",
                    )
                    break
        return list(findings.values())

    def nvd_knows(self, product_versions):
        """False if NVD has no CVEs at all under any of these vendor:product names (likely a wrong name)."""
        index = self.nvd_index()
        return any((v, p) in index for v, p, _ in product_versions)

    def cisco_findings(self, facts):
        os_type = {"IOS": "IOS", "IOS XE": "IOS XE", "ASA": "ASA"}.get(facts.os_name)
        advisories = self.cisco_advisories(os_type, facts.version) if os_type else None
        if advisories is None:
            return None  # not synced for this version
        return [advisory_finding(a, facts) for a in advisories]


def _nvd_match(spellings, ver, si, se, ei, ee):
    if ver not in ("*", "-", ""):
        return ver.lower() in spellings
    if not (si or se or ei or ee):
        return False  # "all versions" entries are too broad to be useful
    v = spellings[-1]
    if si and versions.compare(v, si) < 0:
        return False
    if se and versions.compare(v, se) <= 0:
        return False
    if ei and versions.compare(v, ei) > 0:
        return False
    if ee and versions.compare(v, ee) >= 0:
        return False
    return True


def _same_stream(installed, other):
    """RHEL-family module streams share package names (php 8.0 base, php:8.1/8.2/8.3 modules).
    Only compare versions within the same stream."""
    if not other or other == "0":
        return True
    inst_module, other_module = ".module" in installed, ".module" in other
    if inst_module != other_module:
        return False
    if inst_module:
        def major_minor(v):
            return re.findall(r"\d+", v.split(":")[-1])[:2]
        return major_minor(installed) == major_minor(other)
    return True


_KERNEL_PKG = re.compile(r"^(linux-|kernel)")


def _package_candidates(facts, distro):
    """(package name, version) pairs to look up. Debian/Ubuntu feeds use source packages;
    RPM feeds use binary names. Kernels other than the running one are skipped."""
    seen = set()
    for p in facts.pkg_records:
        source = p.get("source") or ""
        if _KERNEL_PKG.match(p["name"]) and (source.startswith("linux") or source.startswith("kernel")
                                              or p["name"].startswith("kernel")):
            # Kernel CVEs only apply to the running kernel, not to other installed kernels or to
            # header packages (linux-libc-dev, kernel-headers).
            if not facts.kernel:
                continue
            if facts.kernel not in p["name"] and p["version"].split(":")[-1] not in facts.kernel:
                continue
        if distro in ("ubuntu", "debian"):
            pair = (p.get("source") or p["name"], p.get("source_version") or p["version"])
            if pair not in seen:
                seen.add(pair)
                yield pair
        else:
            for pair in ((p["name"], p["version"]), (p.get("source") or "", p["version"])):
                if pair[0] and pair not in seen:
                    seen.add(pair)
                    yield pair
