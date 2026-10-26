"""Online vulnerability feeds: CISA KEV and the Cisco PSIRT openVuln API."""

import json
import os
import time

import requests

from .models import Finding, severity_from_cvss
from .versions import normalize_dotted

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "vulnscan")


class KEVCatalog:
    """The set of CVE IDs that CISA lists as known exploited.

    Downloaded at most once a day and cached. Without network access it falls
    back to the cache, then to the small snapshot shipped in ``data/``.
    """

    def __init__(self, cves, source):
        self.cves = set(cves)
        self.source = source

    def __contains__(self, cve):
        return cve in self.cves

    @classmethod
    def load(cls, offline=False, snapshot_path=None, max_age=86400):
        cache = os.path.join(CACHE_DIR, "kev.json")
        fresh = os.path.exists(cache) and time.time() - os.path.getmtime(cache) < max_age
        if not offline and not fresh:
            try:
                resp = requests.get(KEV_URL, timeout=30)
                resp.raise_for_status()
                os.makedirs(CACHE_DIR, exist_ok=True)
                with open(cache, "w", encoding="utf-8") as f:
                    f.write(resp.text)
                fresh = True
            except (requests.RequestException, OSError):
                pass
        for path, label in ((cache, "CISA KEV (cached download)"), (snapshot_path, "CISA KEV (bundled snapshot)")):
            if path and os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                cves = [v["cveID"] for v in data.get("vulnerabilities", [])]
                return cls(cves, label + f", {len(cves)} CVEs")
        return cls([], "CISA KEV unavailable")


class CiscoOpenVuln:
    """Queries Cisco's openVuln API for advisories affecting an exact software version.

    Needs a free API client from https://developer.cisco.com/psirt/ (set
    CISCO_CLIENT_ID and CISCO_CLIENT_SECRET).
    """

    TOKEN_URL = "https://id.cisco.com/oauth2/default/v1/token"
    API_URL = "https://apix.cisco.com/security/advisories/v2/OSType/{ostype}"
    OS_TYPES = {"IOS": "ios", "IOS XE": "iosxe", "ASA": "asa"}

    def __init__(self, client_id, client_secret, timeout=30):
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self._token = None
        self._cache = {}

    def _get_token(self):
        if self._token is None:
            resp = requests.post(
                self.TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                timeout=self.timeout,
            )
            resp.raise_for_status()
            self._token = resp.json()["access_token"]
        return self._token

    def advisories(self, os_name, version):
        ostype = self.OS_TYPES.get(os_name)
        if not ostype or not version:
            return []
        if ostype == "iosxe":
            version = normalize_dotted(version)
        key = (ostype, version)
        if key not in self._cache:
            resp = requests.get(
                self.API_URL.format(ostype=ostype),
                params={"version": version},
                headers={"Authorization": f"Bearer {self._get_token()}", "Accept": "application/json"},
                timeout=self.timeout,
            )
            if resp.status_code == 404:  # no advisories for this version
                self._cache[key] = []
            else:
                resp.raise_for_status()
                self._cache[key] = resp.json().get("advisories", [])
        return self._cache[key]

    def findings(self, facts):
        results = []
        for adv in self.advisories(facts.os_name, facts.version):
            cves = [c for c in adv.get("cves", []) if c and c != "NA"]
            try:
                cvss = float(adv.get("cvssBaseScore"))
            except (TypeError, ValueError):
                cvss = None
            sir = (adv.get("sir") or "").lower()
            severity = sir if sir in ("critical", "high", "medium", "low") else severity_from_cvss(cvss)
            fixed = ", ".join(adv.get("firstFixed") or []) or "see advisory"
            results.append(
                Finding(
                    id=cves[0] if cves else adv.get("advisoryId", "cisco-advisory"),
                    title=adv.get("advisoryTitle", ""),
                    severity=severity,
                    category="vulnerability",
                    description=f"Cisco advisory {adv.get('advisoryId', '')}",
                    remediation=f"Upgrade to a fixed release (first fixed: {fixed}).",
                    cvss=cvss,
                    cves=cves,
                    evidence=[f"{facts.os_name} {facts.version} listed as affected by Cisco PSIRT"],
                    references=[u for u in [adv.get("publicationUrl")] if u],
                    source="Cisco openVuln API",
                )
            )
        return results
