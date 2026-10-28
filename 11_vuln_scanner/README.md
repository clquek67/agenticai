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

Output is a **self-contained HTML report** (opens offline, prints to PDF, light and dark mode) plus
`findings.json` and `findings.csv`. See `examples/sample-report/report.html`.

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
               --allowlist examples/allowlist.txt --no-network --org "Example Org"
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
vulnscan/scanner.py      orchestration and scoring
vulnscan/report.py       HTML / JSON / CSV output
data/                    rules and reference data
examples/                sample inventory, saved device output and a sample report
```
