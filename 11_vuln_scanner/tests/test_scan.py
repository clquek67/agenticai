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
