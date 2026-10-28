import json
import os

import scan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_offline_scan_end_to_end(tmp_path):
    ex = os.path.join(ROOT, "examples")
    scan.main([
        "--inventory", os.path.join(ex, "devices.csv"),
        "--offline", os.path.join(ex, "offline"),
        "--allowlist", os.path.join(ex, "allowlist.txt"),
        "--no-network", "--out", str(tmp_path),
    ])
    data = json.loads((tmp_path / "findings.json").read_text())
    status = {d["name"]: d["status"] for d in data["devices"]}
    assert status["sw-guest-01"] == "skipped" and status["sw-lab-07"] == "failed"
    wan = next(d for d in data["devices"] if d["name"] == "rtr-wan-01")
    top = wan["findings"][0]
    assert top["id"] == "CVE-2023-20198" and top["kev"] and top["priority"] == "P1"

    html = (tmp_path / "report.html").read_text()
    assert "CVE-2023-20198" in html and "Devices not scanned" in html
    # secrets from the sample configs never reach the outputs
    for secret in ("EXAMPLE-NOT-REAL", "EXAMPLE0000", "$9$EXAMPLEONLY"):
        assert secret not in html and secret not in (tmp_path / "findings.json").read_text()
    assert (tmp_path / "findings.csv").read_text().startswith("device,host")


def test_offline_scan_with_feed_folder(tmp_path):
    ex = os.path.join(ROOT, "examples")
    scan.main([
        "--inventory", os.path.join(ex, "devices.csv"), "--offline", os.path.join(ex, "offline"),
        "--allowlist", os.path.join(ex, "allowlist.txt"), "--feeds", os.path.join(ex, "feeds"), "--out", str(tmp_path),
    ])
    data = json.loads((tmp_path / "findings.json").read_text())
    by_name = {d["name"]: d for d in data["devices"]}
    rocky = {f["id"]: f for f in by_name["web-lnx-02"]["findings"]}
    # real Rocky data: PHP2Shell fixed in the base PHP 8.0 stream by 8.0.30-8.el9_8.1, never a module-stream version
    assert "0:8.0.30-8.el9_8.1" in rocky["CVE-2026-109618"]["remediation"] and rocky["CVE-2026-109618"]["kev"]
    assert not any("module" in f["remediation"] for f in rocky.values())
    assert not by_name["web-lnx-01"]["findings"]  # patched Ubuntu server
    assert "SAMPLE-WIN-0001" in {f["id"] for f in by_name["web-win-01"]["findings"]}
    request = json.loads((tmp_path / "feed-request.json").read_text())
    assert request["distros"] == ["rocky:9", "ubuntu:24.04"] and "ASA|9.8(4)15" in request["cisco_versions"]
    html = (tmp_path / "report.html").read_text()
    assert "Fix plan" in html and "Vulnerability feeds used" in html
