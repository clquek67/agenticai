"""Download vulnerability databases on an internet-connected machine (``scan.py --sync-feeds``).

Each source is downloaded, reduced to what the scanner needs (only the Linux releases,
Windows versions and products you run) and written to the feed folder with a checksum
manifest. Copy the folder to the offline scanner and run ``scan.py --feeds <folder>``.

Sources: OSV.dev (Linux packages), NVD (network devices, PHP), Microsoft MSRC (Windows),
Cisco openVuln (exact Cisco versions), CISA KEV and EPSS. A failure in one source is
recorded in the manifest and the previous copy of that feed is kept.
"""

import csv
import gzip
import hashlib
import io
import json
import logging
import os
import re
import shutil
import tempfile
import time
import zipfile
from datetime import datetime, timedelta, timezone

import requests

from .cvss import base_score
from .feeds import KEV_URL, CiscoOpenVuln

log = logging.getLogger("vulnscan.sync")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OSV_URL = "https://osv-vulnerabilities.storage.googleapis.com/{ecosystem}/all.zip"
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MSRC_URL = "https://api.msrc.microsoft.com/cvrf/v3.0/updates"
EPSS_URLS = [
    "https://epss.empiricalsecurity.com/epss_scores-current.csv.gz",
    "https://epss.cyentia.com/epss_scores-current.csv.gz",
]

DEFAULT_DISTROS = ["ubuntu:20.04", "ubuntu:22.04", "ubuntu:24.04", "debian:11", "debian:12", "debian:13",
                   "rhel:8", "rhel:9", "rocky:8", "rocky:9", "alma:8", "alma:9"]
DEFAULT_WINDOWS = ["Windows Server 2016", "Windows Server 2019", "Windows Server 2022", "Windows Server 2025"]
OSV_ECOSYSTEMS = {"ubuntu": "Ubuntu", "debian": "Debian", "rhel": "Red Hat", "rocky": "Rocky Linux", "alma": "AlmaLinux"}
BUNDLE_PREFIXES = ("USN-", "LSN-", "DSA-", "DLA-", "DTSA-")
SEVERITY_WORDS = {"negligible": "info", "low": "low", "medium": "medium", "moderate": "medium",
                  "important": "high", "high": "high", "critical": "critical"}


def utcnow():
    return datetime.now(timezone.utc)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json_gz(path, data):
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    os.replace(tmp, path)


def read_json_gz(path, default=None):
    if not os.path.exists(path):
        return default
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def severity_label(word=None, score=None):
    if word and word.lower() in SEVERITY_WORDS:
        return SEVERITY_WORDS[word.lower()]
    if score is None:
        return "medium"
    if score >= 9:
        return "critical"
    if score >= 7:
        return "high"
    if score >= 4:
        return "medium"
    return "low" if score > 0 else "info"


# --- OSV (Linux packages) ---------------------------------------------------------

def release_matches(distro_key, ecosystem):
    distro, _, release = distro_key.partition(":")
    if distro == "ubuntu":
        return ecosystem in (f"Ubuntu:{release}:LTS", f"Ubuntu:{release}")
    if distro == "debian":
        return ecosystem == f"Debian:{release}"
    if distro == "rhel":
        return ecosystem.startswith(f"Red Hat:enterprise_linux:{release}::")
    if distro == "rocky":
        return ecosystem == f"Rocky Linux:{release}"
    if distro == "alma":
        return ecosystem == f"AlmaLinux:{release}"
    return False


def compact_osv_record(d):
    """-> (cve ids, severity, cvss, summary) or None for withdrawn records."""
    if d.get("withdrawn"):
        return None
    cves = [c for c in (d.get("upstream", []) + d.get("aliases", [])) if c.startswith("CVE-")]
    if d["id"].startswith("CVE-"):
        cves.insert(0, d["id"])
    cves = list(dict.fromkeys(cves)) or [d["id"]]
    score, word = None, None
    for s in d.get("severity", []):
        if s.get("type") == "CVSS_V3":
            score = base_score(s.get("score"))
        elif s.get("type") == "Ubuntu":
            word = s.get("score")
    summary = (d.get("summary") or d.get("details") or "").strip().replace("\n", " ")[:160]
    return cves, severity_label(word, score), score, summary


def compact_osv_zip(zip_path, distro_keys):
    """Keep fixed vulnerabilities, plus unfixed ones rated high/critical, for the given releases."""
    records, releases, seen = {}, {k: {} for k in distro_keys}, set()
    needles = [_ecosystem_needle(k) for k in distro_keys]
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            raw = z.read(name)
            if not any(n in raw for n in needles):  # cheap skip before parsing JSON
                continue
            if name.startswith(BUNDLE_PREFIXES):  # Ubuntu/Debian also publish one record per CVE: use those
                continue
            d = json.loads(raw)
            info = None
            for a in d.get("affected", []):
                eco = a.get("package", {}).get("ecosystem", "")
                keys = [k for k in distro_keys if release_matches(k, eco)]
                if not keys:
                    continue
                if info is None:
                    info = compact_osv_record(d)
                    if info is None:
                        break
                for r in a.get("ranges", []):
                    if r.get("type") != "ECOSYSTEM":
                        continue
                    introduced = None
                    for ev in r.get("events", []):
                        if "introduced" in ev:
                            introduced = ev["introduced"]
                        elif "fixed" in ev and introduced is not None:
                            _add_range(releases, seen, keys, a["package"]["name"], d["id"], introduced, ev["fixed"])
                            introduced = None
                        elif "last_affected" in ev and introduced is not None:
                            if info[1] in ("high", "critical"):  # affected up to this version, no fix
                                _add_range(releases, seen, keys, a["package"]["name"], d["id"], introduced, None,
                                           ev["last_affected"])
                            introduced = None
                    if introduced is not None and info[1] in ("high", "critical"):  # no fix yet
                        _add_range(releases, seen, keys, a["package"]["name"], d["id"], introduced, None)
            if info is not None:
                records[d["id"]] = list(info)
    used = {e[0] for rel in releases.values() for entries in rel.values() for e in entries}
    return {"records": {k: v for k, v in records.items() if k in used}, "releases": releases}


def _ecosystem_needle(distro_key):
    distro, _, release = distro_key.partition(":")
    return {
        "ubuntu": f'"Ubuntu:{release}', "debian": f'"Debian:{release}"', "rhel": f"enterprise_linux:{release}::",
        "rocky": f'"Rocky Linux:{release}"', "alma": f'"AlmaLinux:{release}"',
    }.get(distro, distro_key).encode()


def _add_range(releases, seen, keys, pkg, osv_id, introduced, fixed, last_affected=None):
    """Entry: [osv_id, introduced, fixed or None, last_affected or None]."""
    for k in keys:
        marker = (k, pkg, osv_id, introduced, fixed, last_affected)
        if marker not in seen:
            seen.add(marker)
            releases[k].setdefault(pkg, []).append([osv_id, introduced, fixed, last_affected])


# --- NVD (network devices and applications) ----------------------------------------

_CPE_SPLIT = re.compile(r"(?<!\\):")


def parse_cpe(criteria):
    parts = _CPE_SPLIT.split(criteria)
    if len(parts) < 6:
        return None
    return parts[3], parts[4], parts[5].replace("\\", "")


def compact_nvd_cve(cve, products):
    """Keep a CVE only if it names one of ``products`` (set of (vendor, product))."""
    matches = []
    for config in cve.get("configurations", []):
        and_config = config.get("operator") == "AND" or len(config.get("nodes", [])) > 1
        for node in config.get("nodes", []):
            for m in node.get("cpeMatch", []):
                if not m.get("vulnerable"):
                    continue
                parsed = parse_cpe(m.get("criteria", ""))
                if not parsed or (parsed[0], parsed[1]) not in products:
                    continue
                matches.append([parsed[0], parsed[1], parsed[2],
                                m.get("versionStartIncluding"), m.get("versionStartExcluding"),
                                m.get("versionEndIncluding"), m.get("versionEndExcluding"), and_config])
    if not matches:
        return None
    score = None
    metrics = cve.get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV40", "cvssMetricV2"):
        if metrics.get(key):
            score = metrics[key][0].get("cvssData", {}).get("baseScore")
            break
    desc = next((d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"), "")
    return {"cvss": score, "sev": severity_label(None, score), "desc": desc.strip()[:200], "matches": matches}


def sync_nvd(out_dir, api_key=None, products_file=None, session=None):
    session = session or requests.Session()
    with open(products_file or os.path.join(DATA_DIR, "nvd_products.json"), encoding="utf-8") as f:
        products = {tuple(p) for p in json.load(f)}
    path = os.path.join(out_dir, "nvd.json.gz")
    store = read_json_gz(path, {"updated": None, "cves": {}})
    headers = {"apiKey": api_key} if api_key else {}
    pause = 0.7 if api_key else 6.5  # NVD rate limits: 50 or 5 requests per 30 s
    now = utcnow()
    params = {"resultsPerPage": 2000}
    last = datetime.fromisoformat(store["updated"]) if store.get("updated") else None
    if last and now - last < timedelta(days=119):
        params["lastModStartDate"] = last.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        params["lastModEndDate"] = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    else:
        store["cves"] = {}  # full download
    start, total = 0, None
    while total is None or start < total:
        resp = _get(session, NVD_URL, params={**params, "startIndex": start}, headers=headers, timeout=120)
        page = resp.json()
        total = page.get("totalResults", 0)
        for item in page.get("vulnerabilities", []):
            cve = item["cve"]
            compact = compact_nvd_cve(cve, products)
            if compact:
                store["cves"][cve["id"]] = compact
            else:
                store["cves"].pop(cve["id"], None)
        start += page.get("resultsPerPage", 2000) or 2000
        log.info("NVD: %d/%d", min(start, total), total)
        if start < total:
            time.sleep(pause)
    store["updated"] = now.isoformat()
    write_json_gz(path, store)
    return "nvd.json.gz", len(store["cves"])


# --- Microsoft (Windows) ------------------------------------------------------------

def compact_cvrf(doc, product_names):
    """-> {product name: [[cve, fixed_build, kb, severity, cvss, title], ...]} for the wanted products."""
    wanted = {}
    for p in doc.get("ProductTree", {}).get("FullProductName", []):
        name = p.get("Value", "")
        base = name.replace(" (Server Core installation)", "")
        if base in product_names:
            wanted[p["ProductID"]] = name
    out = {}
    for v in doc.get("Vulnerability", []):
        cve = v.get("CVE")
        title = (v.get("Title") or {}).get("Value", "")
        sev = {}
        for t in v.get("Threats", []):
            if t.get("Type") == 3:
                for pid in t.get("ProductID", []):
                    sev[pid] = (t.get("Description") or {}).get("Value", "")
        score = {}
        for s in v.get("CVSSScoreSets", []):
            for pid in s.get("ProductID", []):
                score[pid] = s.get("BaseScore")
        for r in v.get("Remediations", []):
            if r.get("Type") != 2 or not r.get("FixedBuild"):
                continue
            kb = (r.get("Description") or {}).get("Value", "")
            for pid in r.get("ProductID", []):
                if pid in wanted:
                    out.setdefault(wanted[pid], []).append(
                        [cve, r["FixedBuild"], kb, severity_label(sev.get(pid), score.get(pid)), score.get(pid), title])
    return out


def sync_msrc(out_dir, products, since_year=2022, session=None):
    session = session or requests.Session()
    path = os.path.join(out_dir, "msrc.json.gz")
    store = read_json_gz(path, {"docs": {}})
    index = _get(session, MSRC_URL, headers={"Accept": "application/json"}, timeout=60).json()
    recent = sorted(index.get("value", []), key=lambda u: u.get("InitialReleaseDate", ""))
    for i, upd in enumerate(recent):
        doc_id = upd.get("ID", "")
        year = int(doc_id[:4]) if doc_id[:4].isdigit() else 0
        if year < since_year:
            continue
        # Re-fetch the last 3 months (Microsoft revises them); older months only if missing.
        if doc_id in store["docs"] and i < len(recent) - 3:
            continue
        doc = _get(session, upd["CvrfUrl"], headers={"Accept": "application/json"}, timeout=120).json()
        store["docs"][doc_id] = compact_cvrf(doc, set(products))
        log.info("MSRC: %s", doc_id)
    write_json_gz(path, store)
    return "msrc.json.gz", sum(len(e) for d in store["docs"].values() for e in d.values())


# --- small feeds --------------------------------------------------------------------

def sync_kev(out_dir, session=None):
    session = session or requests.Session()
    data = _get(session, KEV_URL, timeout=60).json()
    path = os.path.join(out_dir, "kev.json")
    kev = {v["cveID"]: v.get("dateAdded", "") for v in data.get("vulnerabilities", [])}
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"catalogVersion": data.get("catalogVersion"), "cves": kev}, f)
    return "kev.json", len(kev)


def sync_epss(out_dir, session=None):
    session = session or requests.Session()
    last_error = None
    for url in EPSS_URLS:
        try:
            raw = _get(session, url, timeout=120).content
            break
        except requests.RequestException as exc:
            last_error = exc
    else:
        raise last_error
    text = gzip.decompress(raw).decode("utf-8")
    scores = {}
    for row in csv.reader(line for line in io.StringIO(text) if not line.startswith("#")):
        if row and row[0].startswith("CVE-"):
            scores[row[0]] = [float(row[1]), float(row[2])]
    write_json_gz(os.path.join(out_dir, "epss.json.gz"), scores)
    return "epss.json.gz", len(scores)


def sync_cisco(out_dir, versions, client_id, client_secret):
    path = os.path.join(out_dir, "cisco.json")
    store = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            store = json.load(f)
    api = CiscoOpenVuln(client_id, client_secret)
    keep = ("advisoryId", "advisoryTitle", "cves", "cvssBaseScore", "sir", "firstFixed", "publicationUrl")
    for item in versions:
        os_name, _, version = item.partition("|")
        advisories = api.advisories(os_name, version)
        store[item] = [{k: a.get(k) for k in keep} for a in advisories]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f)
    return "cisco.json", len(store)


def _get(session, url, **kwargs):
    for attempt in range(4):
        try:
            resp = session.get(url, **kwargs)
            if resp.status_code in (429, 503):
                raise requests.HTTPError(f"{resp.status_code} rate limited", response=resp)
            resp.raise_for_status()
            return resp
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 2))


def _download(session, url, dest):
    with session.get(url, stream=True, timeout=600) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            shutil.copyfileobj(resp.raw, f, 1 << 20)


# --- orchestration ------------------------------------------------------------------

WINDOWS_NAMES = {"2012": "Windows Server 2012", "2012r2": "Windows Server 2012 R2", "2016": "Windows Server 2016",
                 "2019": "Windows Server 2019", "2022": "Windows Server 2022", "2025": "Windows Server 2025"}
CISCO_OS = ("IOS", "IOS XE", "ASA")


def normalize_request(req):
    """Check and tidy a request: 'ubuntu:24.04', 'Windows Server 2019' (or '2019'), 'IOS XE|17.9.4a'."""
    out, errors = {"distros": set(), "windows_products": set(), "cisco_versions": set()}, []
    for d in req.get("distros", []):
        d = d.strip().lower()
        family, _, release = d.partition(":")
        if family in OSV_ECOSYSTEMS and release:
            out["distros"].add(d)
        else:
            errors.append(f"distro '{d}' (use e.g. ubuntu:24.04, debian:12, rhel:9, rocky:9, alma:9)")
    for w in req.get("windows_products", []):
        key = w.strip().lower().replace("windows server", "").replace(" ", "")
        if key in WINDOWS_NAMES:
            out["windows_products"].add(WINDOWS_NAMES[key])
        else:
            errors.append(f"Windows version '{w}' (use 2016, 2019, 2022, 2025, 2012r2)")
    for c in req.get("cisco_versions", []):
        os_name, sep, version = c.partition("|")
        os_name = {"IOSXE": "IOS XE", "IOS-XE": "IOS XE"}.get(os_name.strip().upper(), os_name.strip().upper())
        if sep and os_name in CISCO_OS and version.strip():
            out["cisco_versions"].add(f"{os_name}|{version.strip()}")
        else:
            errors.append(f"Cisco version '{c}' (use e.g. IOS XE|17.9.4a, IOS|15.2(7)E8, ASA|9.16(4))")
    if errors:
        raise ValueError("Not understood: " + "; ".join(errors))
    return {k: sorted(v) for k, v in out.items()}


def load_request(out_dir, request_files=(), extra=None):
    """Merge scanner requests (feed-request.json files) and command-line additions into the
    feed folder's saved request, which is remembered for later syncs."""
    if isinstance(request_files, str):
        request_files = [request_files]
    path = os.path.join(out_dir, "request.json")
    req = {"distros": [], "windows_products": [], "cisco_versions": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            req.update(json.load(f))
    sources = []
    for request_file in request_files or []:
        with open(request_file, encoding="utf-8") as f:
            sources.append(json.load(f))
    if extra:
        sources.append(extra)
    for new in sources:
        for key in req:
            req[key] = sorted(set(req[key]) | set(new.get(key, [])))
    req = normalize_request(req)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(req, f, indent=2)
    return req


def sync_all(out_dir, request_file=None, distros=None, skip=(), nvd_api_key=None, msrc_since=2022,
             cisco_id=None, cisco_secret=None, windows=None, cisco_versions=None):
    os.makedirs(out_dir, exist_ok=True)
    extra = {"distros": distros or [], "windows_products": windows or [], "cisco_versions": cisco_versions or []}
    req = load_request(out_dir, request_file, extra)
    distros = req["distros"] or DEFAULT_DISTROS
    windows = sorted(set(req["windows_products"])) or DEFAULT_WINDOWS
    manifest_path = os.path.join(out_dir, "manifest.json")
    manifest = {"feeds": {}}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    session = requests.Session()

    jobs = []
    if "osv" not in skip:
        for family in sorted({d.split(":")[0] for d in distros if d.split(":")[0] in OSV_ECOSYSTEMS}):
            keys = [d for d in distros if d.startswith(family + ":")]
            jobs.append((f"osv-{family}", lambda family=family, keys=keys: _sync_osv(out_dir, family, keys, session)))
    if "kev" not in skip:
        jobs.append(("kev", lambda: sync_kev(out_dir, session)))
    if "epss" not in skip:
        jobs.append(("epss", lambda: sync_epss(out_dir, session)))
    if "nvd" not in skip:
        jobs.append(("nvd", lambda: sync_nvd(out_dir, nvd_api_key, session=session)))
    if "msrc" not in skip:
        jobs.append(("msrc", lambda: sync_msrc(out_dir, windows, msrc_since, session)))
    if "cisco" not in skip:
        if cisco_id and cisco_secret and req["cisco_versions"]:
            jobs.append(("cisco", lambda: sync_cisco(out_dir, req["cisco_versions"], cisco_id, cisco_secret)))
        elif not req["cisco_versions"]:
            log.warning("Cisco: no versions requested yet; run a scan and bring back feed-request.json")
        else:
            log.warning("Cisco: CISCO_CLIENT_ID / CISCO_CLIENT_SECRET not set, skipped")

    for name, job in jobs:
        entry = manifest["feeds"].get(name, {})
        print(f"  {name} ...", end="", flush=True)
        try:
            filename, records = job()
            entry.update(file=filename, sha256=sha256(os.path.join(out_dir, filename)), records=records,
                         updated=utcnow().isoformat(timespec="seconds"), status="ok", error="")
            print(f" ok ({records} records)")
        except Exception as exc:  # keep the previous copy and carry on with the other feeds
            entry.update(status="error", error=f"{type(exc).__name__}: {exc}"[:300],
                         attempted=utcnow().isoformat(timespec="seconds"))
            print(f" FAILED: {entry['error']}")
        manifest["feeds"][name] = entry
    manifest["created"] = utcnow().isoformat(timespec="seconds")
    manifest["distros"] = distros
    manifest["windows_products"] = windows
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def _sync_osv(out_dir, family, keys, session):
    with tempfile.TemporaryDirectory(dir=out_dir) as tmp:
        zpath = os.path.join(tmp, "all.zip")
        _download(session, OSV_URL.format(ecosystem=OSV_ECOSYSTEMS[family].replace(" ", "%20")), zpath)
        data = compact_osv_zip(zpath, keys)
    filename = f"osv-{family}.json.gz"
    write_json_gz(os.path.join(out_dir, filename), data)
    return filename, sum(len(v) for rel in data["releases"].values() for v in rel.values())
