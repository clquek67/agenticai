# 11 · VulnScan: credentialed network vulnerability scanner

A command-line scanner, in the spirit of Tenable Nessus, for network devices. It logs in with a
**read-only** account, reads the exact model, software version and running configuration, then reports:

- **Known vulnerabilities (CVEs)**: from the Cisco PSIRT openVuln API (live, exact-version match) and
  local advisory rules in `data/advisories.json`. A rule can require the vulnerable feature to be
  enabled in the config (e.g. the IOS XE web UI for CVE-2023-20198), which cuts false positives.
- **Actively exploited CVEs**: flagged from the CISA Known Exploited Vulnerabilities (KEV) catalog.
- **Configuration weaknesses**: 26 hardening rules in `data/config_rules.json` (Telnet, default
  SNMP communities, plain-text passwords, HTTP management, any-any firewall rules, no syslog/NTP, ...).
- **End of sale / end of support hardware** from `data/lifecycle.json`.

With a feed folder (below) it reports **every published CVE** for each device, grouped into a
fix plan ("update php8.3: fixes 12 CVEs, 1 actively exploited").

Output is a **self-contained HTML report** (opens offline, prints to PDF, light and dark mode) plus
`findings.json` and `findings.csv`. See `examples/sample-report/report.html`.

## Offline vulnerability feeds (two-machine setup)

The scanner can match **every published CVE** for the devices it scans without itself having
internet access. A separate *sync machine* downloads the databases; you copy the folder across.

```
 Sync machine (internet)                     Scanner (no internet)                 Devices
 python scan.py --sync-feeds --out feeds  →  python scan.py ... --feeds feeds   →  SSH / WinRM
            ▲                                          │
            └──────── feed-request.json ◄──────────────┘  (OS releases + software versions only)
```

| Feed | Covers | Source |
|---|---|---|
| `osv-<distro>` | every package on Ubuntu, Debian, RHEL, Rocky, Alma, using the distribution's own fixed versions (backports handled) | OSV.dev bulk download |
| `msrc` | Windows Server 2016/2019/2022/2025 CVEs and the cumulative-update build that fixes each | Microsoft Security Update Guide (CVRF API) |
| `nvd` | Cisco (fallback), Fortinet, Juniper, Aruba, Comware, PHP and the products in `data/nvd_products.json` | NIST NVD API 2.0 |
| `cisco` | exact Cisco IOS / IOS XE / ASA versions you run | Cisco openVuln API |
| `kev` | which CVEs are exploited in the wild | CISA KEV |
| `epss` | probability each CVE is exploited in the next 30 days | FIRST EPSS |

Only these outbound HTTPS hosts are needed **on the sync machine**: `osv-vulnerabilities.storage.googleapis.com`,
`services.nvd.nist.gov`, `api.msrc.microsoft.com`, `id.cisco.com`, `apix.cisco.com`, `www.cisa.gov`,
`epss.empiricalsecurity.com`. It needs no access to your devices and holds no device credentials.

**Workflow**

1. On the sync machine (first time, before any scan has run):
   ```bash
   export NVD_API_KEY=...            # free: https://nvd.nist.gov/developers/request-an-api-key
   export CISCO_CLIENT_ID=... CISCO_CLIENT_SECRET=...   # free: https://developer.cisco.com/psirt/
   python scan.py --sync-feeds --out feeds --distros ubuntu:22.04,ubuntu:24.04,rhel:9,rocky:9
   ```
   The first run downloads a few GB and takes 20-60 minutes (NVD is the slow part); later runs
   only fetch changes. The resulting folder is small (tens of MB).
2. Copy the whole `feeds` folder to the scanner (file share, transfer server or USB).
3. On the scanner: `python scan.py --inventory devices.csv --credentials credentials.yaml --allowlist allowlist.txt --feeds feeds`.
   Every file is checked against the checksums in `feeds/manifest.json`; a changed or partial
   copy is refused. Feeds older than 7 days are flagged in the report.
4. Each scan writes `feed-request.json` next to the report: the Linux releases, Windows versions
   and Cisco software versions it found (no IP addresses, hostnames or configs). Copy it back and
   run `python scan.py --sync-feeds --out feeds --request feed-request.json` so the next sync
   includes them. The feed folder remembers earlier requests.

**Daily schedule on the sync machine**

Linux (cron, 05:15 every day):
```
15 5 * * * cd /opt/vulnscan && .venv/bin/python scan.py --sync-feeds --out /srv/vulnscan-feeds >> sync.log 2>&1
```
Windows (Task Scheduler, run as a service account):
```powershell
schtasks /Create /TN "VulnScan feed sync" /SC DAILY /ST 05:15 /RU "DOMAIN\svc-vulnsync" /RP * ^
  /TR "C:\vulnscan\.venv\Scripts\python.exe C:\vulnscan\scan.py --sync-feeds --out D:\vulnscan-feeds"
```
Then sync the feed folder to the scanner with whatever your transfer process is (e.g. `robocopy`/`rsync`
to a share the scanner can read).

A failed source (e.g. NVD down) is recorded in the manifest and its previous copy is kept, so the
scanner keeps working with slightly older data and says so in the report.

## Supported platforms (v0.1)

| `platform` | Devices | Commands run |
|---|---|---|
| `cisco_ios` | IOS and IOS XE: 2811, 2960X, 3750G, ISR 4331, ... | `show version`, `show running-config` |
| `cisco_asa` | ASA 5512-X, 5520, 5525-X, ... | `show version`, `show running-config` |
| `hpe_comware` | Comware 5/7: 5130, 5500, A5500, 5510, 5900, 5700, 5940, HP 850 | `display version`, `display current-configuration` |
| `linux` | Ubuntu, Debian, RHEL, Rocky, Alma (SSH, no sudo needed) | `cat /etc/os-release`, `php -v` / `php -i`, package list and changelogs, process list |
| `windows` | Windows Server (WinRM over HTTPS) | one read-only PowerShell script: OS info, PHP on PATH / IIS FastCGI / common folders, `php -v` / `php -i` |

### PHP on servers (PHP2Shell: CVE-2026-109618, CVE-2026-109619)

The `linux` and `windows` platforms find every PHP install on a server (PATH, IIS FastCGI, Remi,
Plesk, cPanel, XAMPP, ...) and check it against the PHP2Shell fixes: **8.5.12, 8.4.27, 8.3.36 and
8.2.35**. PHP 8.1 and older have no official fix and are also reported as end of life.

Linux distributions (Ubuntu, Debian, RHEL) backport fixes without changing the PHP version number,
so for distribution packages the scanner reads the package changelog: if it lists the CVE, the
server is reported as fixed. The report also shows whether the partial interim mitigation
(`session.upload_progress.enabled = 0`) is in place in the CLI `php.ini`.

Windows needs WinRM (HTTPS, port 5986) enabled and an account in *Remote Management Users*.

Next modules planned: Aruba (AOS-CX, ArubaOS, ArubaOS-Switch, ClearPass), Juniper Junos, TippingPoint.

## Safety

- Only `show` / `display` commands are sent; the SSH collector refuses anything else.
- A live scan **requires an allowlist** of approved networks; hosts outside it are skipped.
- 5 devices at a time by default (`--workers`), gentle on firewalls and switches.
- Passwords come from environment variables, never the inventory or credentials file.
- Full configurations stay in memory only; secrets in report evidence are masked.

Only scan devices you own or are authorised in writing to assess.

## Quick start

```bash
cd 11_vuln_scanner
pip install -r requirements.txt

# Offline demo with the sample devices in examples/ (no network needed)
python scan.py --inventory examples/devices.csv --offline examples/offline \
               --allowlist examples/allowlist.txt --feeds examples/feeds --org "Example Org"
```

## Live scan

1. Create read-only accounts on the devices (Cisco: an account that can run `show running-config`;
   Comware: a `network-operator` / level-1+ user with SSH).
2. Write the inventory CSV (`host,name,platform,credential,site`), see `examples/devices.csv`.
3. Copy `examples/credentials.example.yaml` to `credentials.yaml` and export the passwords:
   ```bash
   export VULNSCAN_CISCO_PASSWORD='...'  VULNSCAN_CISCO_ENABLE='...'
   export VULNSCAN_ASA_PASSWORD='...'    VULNSCAN_ASA_ENABLE='...'
   export VULNSCAN_COMWARE_PASSWORD='...'
   export VULNSCAN_LINUX_PASSWORD='...'  VULNSCAN_WINDOWS_PASSWORD='...'
   ```
4. Optional but recommended: get a free Cisco openVuln API client at
   https://developer.cisco.com/psirt/ and export `CISCO_CLIENT_ID` / `CISCO_CLIENT_SECRET`.
5. Run it from a host that can reach the devices' management IPs:
   ```bash
   python scan.py --inventory devices.csv --credentials credentials.yaml \
                  --allowlist allowlist.txt --org "My Company" -v
   ```
   The report is written to `reports/scan-<timestamp>/report.html`.

You can also scan output you already have: save it as `<dir>/<host>/version.txt` and
`<dir>/<host>/config.txt` and use `--offline <dir>`.

## Adding knowledge

**Advisory rule** (`data/advisories.json`). Use this for vendors without an API, such as HPE Comware,
copying fixed releases from the vendor's security bulletin:

```json
{
  "id": "CVE-XXXX-YYYY",
  "platform": "hpe_comware",
  "model_regex": "^5130",
  "title": "Short description",
  "cvss": 7.5,
  "affected": {"field": "release", "fixed_in": "3507P10"},
  "requires_config": "^\\s*ip http enable",
  "remediation": "Upgrade to Release 3507P10 or later.",
  "references": ["https://support.hpe.com/..."]
}
```

`affected` supports `version_regex`, `fixed_in`, `fixed_by_train` (fixed release per train, e.g.
`{"17.9": "17.9.4a"}`), `introduced`, `not_affected_from` and `field` (`version` or `release`).
No Comware CVE rules ship yet: add them from HPE bulletins for the releases you run.

**Config rule** (`data/config_rules.json`): `type` `present` fires when the regex matches the running
config, `absent` when it doesn't.

**Software rules**: advisories with `"software": "php"` and `"platforms": ["linux", "windows"]`
are checked against each PHP install found on a server (`data/advisories.json`);
`data/software_lifecycle.json` sets the oldest supported PHP branch.

**Lifecycle** (`data/lifecycle.json`): model regex → `end_of_support` / `end_of_sale` / `supported`.
Confirm dates against the vendor's end-of-life notices.

**New platform**: subclass `Platform` in `vulnscan/platforms.py` (Netmiko device type, commands,
parser) and register it in `PLATFORMS`.

## Tests

```bash
python -m pytest -q
```

## Layout

```
scan.py                  CLI
vulnscan/platforms.py    per-vendor commands and parsers
vulnscan/collectors.py   SSH (Netmiko) and offline collectors
vulnscan/checks.py       config rules, local advisories, lifecycle, secret masking
vulnscan/feeds.py        CISA KEV and Cisco openVuln clients
vulnscan/feedsync.py     --sync-feeds: download and compact OSV, NVD, MSRC, Cisco, KEV, EPSS
vulnscan/feedstore.py    --feeds: verify the feed folder and match devices against it
vulnscan/vercmp.py       dpkg / rpm / Windows build version comparison
vulnscan/cvss.py         CVSS v3 base score from a vector
vulnscan/scanner.py      orchestration and scoring
vulnscan/report.py       HTML / JSON / CSV output
data/                    rules and reference data
examples/                sample inventory, saved device output and a sample report
```
