"""Write the scan results: a self-contained HTML report plus JSON and CSV exports."""

import csv
import json
import os
from collections import Counter
from html import escape

from . import __version__
from .models import SEVERITIES
from .platforms import PLATFORMS

SEV_LABEL = {s: s.capitalize() for s in SEVERITIES}
LIFECYCLE_LABEL = {
    "end_of_support": "End of support",
    "end_of_sale": "End of sale",
    "supported": "Supported",
    "unknown": "Check with vendor",
}


def write_all(scan, out_dir, title="Vulnerability Assessment Report", org=""):
    os.makedirs(out_dir, exist_ok=True)
    paths = {
        "html": os.path.join(out_dir, "report.html"),
        "json": os.path.join(out_dir, "findings.json"),
        "csv": os.path.join(out_dir, "findings.csv"),
    }
    with open(paths["html"], "w", encoding="utf-8") as f:
        f.write(render_html(scan, title, org))
    with open(paths["json"], "w", encoding="utf-8") as f:
        json.dump(to_dict(scan), f, indent=2)
    write_csv(scan, paths["csv"])
    return paths


# --- machine-readable exports --------------------------------------------------

def _finding_dict(f):
    return {
        "id": f.id, "title": f.title, "severity": f.severity, "priority": f.priority,
        "category": f.category, "cvss": f.cvss, "cves": f.cves, "kev": f.kev,
        "description": f.description, "remediation": f.remediation,
        "evidence": f.evidence, "references": f.references, "source": f.source,
    }


def to_dict(scan):
    return {
        "scanner": f"VulnScan {__version__}",
        "started": scan.started.isoformat(),
        "finished": scan.finished.isoformat(),
        "risk_score": scan.risk_score(),
        "severity_counts": scan.severity_counts(),
        "kev_count": scan.kev_count(),
        "devices": [
            {
                "host": r.device.host, "name": r.device.name, "site": r.device.site,
                "platform": r.device.platform, "status": r.status, "error": r.error,
                "hostname": r.facts.hostname, "model": r.facts.model, "os": r.facts.os_name,
                "version": r.facts.version, "release": r.facts.release, "serial": r.facts.serial,
                "lifecycle": r.lifecycle, "notes": r.notes, "software": r.facts.software,
                "findings": [_finding_dict(f) for f in r.findings],
            }
            for r in scan.results
        ],
    }


def write_csv(scan, path):
    cols = ["device", "host", "site", "model", "version", "priority", "severity", "id", "title",
            "cvss", "kev", "category", "remediation"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r, fd in scan.all_findings():
            version = " ".join(v for v in (r.facts.version, r.facts.release) if v)
            w.writerow([r.device.label, r.device.host, r.device.site, r.facts.model, version, fd.priority,
                        fd.severity, fd.id, fd.title, fd.cvss if fd.cvss is not None else "",
                        "yes" if fd.kev else "", fd.category, fd.remediation])


# --- HTML ------------------------------------------------------------------------

def _e(value):
    return escape(str(value if value is not None else ""))


def _sev(sev):
    return f'<span class="pill sev-{_e(sev)}">{_e(SEV_LABEL.get(sev, sev))}</span>'


def _kev(flag):
    return '<span class="kev">KEV</span>' if flag else '<span class="muted">—</span>'


def _summary_text(scan):
    counts = scan.severity_counts()
    n_ok, n_all = len(scan.scanned), len(scan.results)
    score = scan.risk_score()
    level = "Critical" if score >= 80 else "High" if score >= 60 else "Moderate" if score >= 30 else "Low"
    parts = [
        f"This scan logged in to <strong>{n_ok} of {n_all} devices</strong> and found "
        f"<strong>{counts['critical']} critical</strong> and <strong>{counts['high']} high</strong> severity issues. "
        f"Overall risk is <strong>{level} ({score}/100)</strong>."
    ]
    kev = scan.kev_count()
    if kev:
        parts.append(f"<strong>{kev} findings are on CISA's Known Exploited Vulnerabilities list</strong>: "
                     "attackers are using them now, so fix these first.")
    eol = [r for r in scan.scanned if r.lifecycle == "end_of_support"]
    if eol:
        parts.append(f"<strong>{len(eol)} devices are past vendor end of support</strong> and will not receive "
                     "security fixes; they belong on the hardware refresh list.")
    if scan.not_scanned:
        parts.append(f"{len(scan.not_scanned)} devices could not be scanned (see section 6).")
    return " ".join(parts)


CSS = """
:root{--bg:#F4F5F7;--card:#FFFFFF;--ink:#101828;--muted:#475467;--line:#E2E5EA;--head:#0F172A;--head-ink:#FFFFFF;--accent:#1D4ED8;
--crit-bg:#FEE4E2;--crit:#912018;--high-bg:#FFEAD5;--high:#93370D;--med-bg:#FEF0C7;--med:#7A4A00;--low-bg:#D1E9FF;--low:#1849A9;--info-bg:#EAECF0;--info:#344054;
--ok-bg:#DCFAE6;--ok:#085D3A;--code-bg:#F2F4F7}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0B1120;--card:#111827;--ink:#F2F4F7;--muted:#A9B1BE;--line:#273244;--head:#020617;--accent:#7AA2F7;
--crit-bg:#55160C;--crit:#FECDCA;--high-bg:#511C10;--high:#FEB273;--med-bg:#4E3A0B;--med:#FEDF89;--low-bg:#102A56;--low:#B2DDFF;--info-bg:#1F2937;--info:#D0D5DD;--ok-bg:#053321;--ok:#A6F4C5;--code-bg:#1F2937}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent)}
header{background:var(--head);color:var(--head-ink);padding:32px 16px}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
header .wrap{padding:0}
header h1{margin:6px 0;font-size:28px;line-height:1.2}
header p{margin:0;color:#CBD5E1}
main.wrap{padding:24px 16px 48px;display:flex;flex-direction:column;gap:24px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px}
h2{margin:0 0 12px;font-size:18px}
h3{margin:0;font-size:15px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;background:none;border:0;padding:0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi b{display:block;font-size:30px;line-height:1.2}
.kpi span{color:var(--muted);font-size:13px}
.muted{color:var(--muted)}
.table{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px}
th{text-align:left;color:var(--muted);font-size:12px;font-weight:600;padding:9px 10px;border-bottom:2px solid var(--line);white-space:nowrap}
td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.pill{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;white-space:nowrap}
.sev-critical{background:var(--crit-bg);color:var(--crit)}.sev-high{background:var(--high-bg);color:var(--high)}
.sev-medium{background:var(--med-bg);color:var(--med)}.sev-low{background:var(--low-bg);color:var(--low)}.sev-info{background:var(--info-bg);color:var(--info)}
.lc-end_of_support{background:var(--crit-bg);color:var(--crit)}.lc-end_of_sale{background:var(--high-bg);color:var(--high)}
.lc-supported{background:var(--ok-bg);color:var(--ok)}.lc-unknown{background:var(--info-bg);color:var(--info)}
.kev{display:inline-block;font-size:11px;font-weight:700;padding:2px 7px;border-radius:5px;background:var(--ink);color:var(--card)}
.bar{display:flex;height:16px;border-radius:6px;overflow:hidden;gap:2px;margin:6px 0 10px}
.bar div{min-width:3px}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:13px}
details{border:1px solid var(--line);border-radius:10px;margin-top:10px}
summary{cursor:pointer;padding:12px 14px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"\\25B8";color:var(--muted)}
details[open] summary::before{content:"\\25BE"}
.dev-body{padding:0 14px 14px}
.finding{border-top:1px solid var(--line);padding:12px 0}
.finding p{margin:4px 0;overflow-wrap:anywhere}
summary span,summary h3{overflow-wrap:anywhere;min-width:0}
code,.mono{font-family:"IBM Plex Mono",ui-monospace,Consolas,monospace;font-size:12px}
.evidence{background:var(--code-bg);border-radius:6px;padding:8px 10px;margin:6px 0;white-space:pre-wrap;word-break:break-word}
footer{color:var(--muted);font-size:12px;text-align:center;padding:0 16px 32px}
@media print{body{background:#fff}section,.kpi{break-inside:avoid}details{display:block}details>*{display:block}summary::before{content:""}}
"""


def render_html(scan, title, org):
    counts = scan.severity_counts()
    total = sum(counts.values()) or 1
    out = []
    w = out.append

    w("<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    w("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    w(f"<title>{_e(title)}</title><style>{CSS}</style></head><body>")
    w("<header><div class='wrap'>")
    w(f"<p>VulnScan {__version__} · credentialed, read-only scan</p><h1>{_e(title)}</h1>")
    when = scan.finished.astimezone().strftime("%d %b %Y %H:%M")
    w(f"<p>{_e(org + ' · ') if org else ''}Scan finished {when} · {len(scan.results)} devices in scope</p>")
    w("</div></header><main class='wrap'>")

    # 1. summary
    w(f"<section><h2>1. Executive summary</h2><p>{_summary_text(scan)}</p></section>")
    w("<div class='kpis'>")
    for label, value, sub in (
        ("Risk score", f"{scan.risk_score()}<small class='muted'>/100</small>", "Higher means more exposed"),
        ("Critical", counts["critical"], "CVSS 9.0+"),
        ("High", counts["high"], "CVSS 7.0–8.9 or serious misconfig"),
        ("Actively exploited", scan.kev_count(), "On CISA KEV list"),
        ("Devices scanned", f"{len(scan.scanned)}<small class='muted'>/{len(scan.results)}</small>", "Logged in successfully"),
    ):
        w(f"<div class='kpi'><span>{label}</span><b>{value}</b><span>{sub}</span></div>")
    w("</div>")

    # 2. severity bar
    colors = {"critical": "#B42318", "high": "#E8590C", "medium": "#F5B83D", "low": "#5B8DEF", "info": "#98A2B3"}
    w("<section><h2>2. Findings by severity</h2>")
    aria = ", ".join(f"{SEV_LABEL[s]} {counts[s]}" for s in SEVERITIES)
    w(f"<div class='bar' role='img' aria-label='{_e(aria)}'>")
    for s in SEVERITIES:
        if counts[s]:
            w(f"<div style='flex:{counts[s] / total:.4f};background:{colors[s]}'></div>")
    w("</div><div class='legend'>")
    for s in SEVERITIES:
        w(f"<span>{_sev(s)} {counts[s]}</span>")
    w("</div></section>")

    # 3. top risks
    w("<section><h2>3. Top risks: fix these first</h2><div class='table'><table>")
    w("<thead><tr><th>Priority</th><th>Severity</th><th>Issue</th><th>Devices</th><th>Exploited</th><th>Fix</th></tr></thead><tbody>")
    issues = scan.grouped_issues()
    for g in issues[:15]:
        f = g["finding"]
        cvss = f" · CVSS {f.cvss}" if f.cvss is not None else ""
        w(f"<tr><td><b>{f.priority}</b></td><td>{_sev(f.severity)}</td>"
          f"<td><b>{_e(f.title)}</b><div class='mono muted'>{_e(f.id)}{cvss}</div></td>"
          f"<td>{len(g['devices'])}<div class='muted'>{_e(', '.join(g['devices'][:4]))}{'…' if len(g['devices']) > 4 else ''}</div></td>"
          f"<td>{_kev(f.kev)}</td><td>{_e(f.remediation)}</td></tr>")
    if not issues:
        w("<tr><td colspan='6' class='muted'>No findings.</td></tr>")
    w("</tbody></table></div>")
    if len(issues) > 15:
        w(f"<p class='muted'>{len(issues) - 15} more issues are listed per device in section 5 and in findings.csv.</p>")
    w("</section>")

    # 4. by platform
    w("<section><h2>4. Results by platform</h2><div class='table'><table>")
    w("<thead><tr><th>Platform</th><th>Devices</th><th>Scanned</th><th>Critical</th><th>High</th><th>Medium</th><th>End of support</th></tr></thead><tbody>")
    for name, plat in PLATFORMS.items():
        rs = [r for r in scan.results if r.device.platform == name]
        if not rs:
            continue
        ok = [r for r in rs if r.status == "ok"]
        c = Counter(f.severity for r in ok for f in r.findings)
        eol = sum(1 for r in ok if r.lifecycle == "end_of_support")
        w(f"<tr><td><b>{_e(plat.label)}</b></td><td>{len(rs)}</td><td>{len(ok)}</td><td>{c['critical']}</td>"
          f"<td>{c['high']}</td><td>{c['medium']}</td><td>{eol}</td></tr>")
    w("</tbody></table></div></section>")

    # 5. per device
    w("<section><h2>5. Findings by device</h2>")
    for r in sorted(scan.scanned, key=lambda r: (min((f.sort_key() for f in r.findings), default=("P9",)), r.device.label)):
        c = Counter(f.severity for f in r.findings)
        version = " ".join(v for v in (r.facts.version, f"Release {r.facts.release}" if r.facts.release else "") if v)
        badges = " ".join(f"{_sev(s)}&nbsp;{c[s]}" for s in SEVERITIES[:3] if c[s])
        w("<details><summary>")
        w(f"<h3>{_e(r.device.label)}</h3><span class='muted mono'>{_e(r.device.host)}</span>"
          f"<span>{_e(r.facts.model)} · {_e(r.facts.os_name)} {_e(version)}</span>"
          f"<span class='pill lc-{_e(r.lifecycle)}'>{_e(LIFECYCLE_LABEL.get(r.lifecycle, r.lifecycle))}</span>{badges}")
        w("</summary><div class='dev-body'>")
        for note in r.notes:
            w(f"<p class='muted'>Note: {_e(note)}</p>")
        if r.facts.software:
            items = "".join(f"<li class='mono'>{_e(i['path'])}: {_e(i['name'].upper())} {_e(i['build'])} ({_e(i['sapi'])})</li>"
                            for i in r.facts.software)
            w(f"<p><b>Software found:</b></p><ul style='margin:4px 0 8px'>{items}</ul>")
        if not r.findings:
            w("<p class='muted'>No findings.</p>")
        for f in r.findings:
            cvss = f" · CVSS {f.cvss}" if f.cvss is not None else ""
            w("<div class='finding'>")
            w(f"<p>{_sev(f.severity)} <b>{f.priority}</b> {_kev(f.kev) if f.kev else ''} <b>{_e(f.title)}</b> "
              f"<span class='mono muted'>{_e(f.id)}{cvss}</span></p>")
            if f.description:
                w(f"<p>{_e(f.description)}</p>")
            if f.evidence:
                w(f"<div class='evidence mono'>{_e(chr(10).join(f.evidence))}</div>")
            if f.remediation:
                w(f"<p><b>Fix:</b> {_e(f.remediation)}</p>")
            if f.references:
                links = " · ".join(f"<a href='{_e(u)}'>{_e(u)}</a>" for u in f.references)
                w(f"<p class='muted'>{links}</p>")
            w(f"<p class='muted'>Source: {_e(f.source)}</p></div>")
        w("</div></details>")
    if not scan.scanned:
        w("<p class='muted'>No devices were scanned successfully.</p>")
    w("</section>")

    # 6. coverage gaps
    w("<section><h2>6. Devices not scanned</h2>")
    if scan.not_scanned:
        w("<div class='table'><table><thead><tr><th>Device</th><th>Host</th><th>Platform</th><th>Status</th><th>Reason</th></tr></thead><tbody>")
        for r in scan.not_scanned:
            w(f"<tr><td>{_e(r.device.label)}</td><td class='mono'>{_e(r.device.host)}</td><td>{_e(r.device.platform)}</td>"
              f"<td>{_e(r.status)}</td><td>{_e(r.error)}</td></tr>")
        w("</tbody></table></div>")
    else:
        w("<p>All devices in the inventory were scanned.</p>")
    w("</section>")

    # 7. method
    rc = scan.rule_counts
    cisco = "Cisco openVuln API (live)" if scan.cisco_api_used else "Cisco openVuln API not configured: Cisco CVEs come from local rules only"
    w("<section><h2>7. Method and data sources</h2><p>Each device was accessed with a read-only account. "
      "Only read-only commands were run (<code>show</code> / <code>display</code> on network devices, inventory queries such as <code>php -v</code> on servers); no exploits were attempted and no configuration "
      "was changed. Full configurations are not stored in this report and secrets in evidence are masked.</p>")
    w(f"<p class='muted'>Sources: {_e(cisco)} · {_e(scan.kev_source)} · {rc['advisories']} local advisory rules · "
      f"{rc['config']} configuration rules · {rc['lifecycle']} lifecycle entries. "
      "Risk score = weighted findings per scanned device (critical 10, high 4, medium 1.5, low 0.3, +10 if actively exploited), "
      "scaled to 0–100.</p></section>")
    w("</main><footer>Generated by VulnScan. Confidential: contains details of security weaknesses.</footer></body></html>")
    return "".join(out)
