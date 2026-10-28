import gzip
import json
import os

import pytest

from vulnscan.feedstore import FeedError, FeedStore, feed_request
from vulnscan.feedsync import compact_cvrf, compact_nvd_cve, load_request, sha256
from vulnscan.models import Device, DeviceResult, Facts

# Minimal documents in the shape Microsoft (CVRF) and NVD (API 2.0) publish.
CVRF = {
    "ProductTree": {"FullProductName": [
        {"ProductID": "11", "Value": "Windows Server 2022"},
        {"ProductID": "12", "Value": "Windows Server 2022 (Server Core installation)"},
        {"ProductID": "99", "Value": "Microsoft Office 2019"},
    ]},
    "Vulnerability": [{
        "CVE": "CVE-2026-0001", "Title": {"Value": "Windows TCP/IP Remote Code Execution Vulnerability"},
        "Threats": [{"Type": 3, "Description": {"Value": "Critical"}, "ProductID": ["11", "12"]}],
        "CVSSScoreSets": [{"BaseScore": 9.8, "ProductID": ["11", "12"]}],
        "Remediations": [
            {"Type": 2, "Description": {"Value": "5066666"}, "ProductID": ["11", "12"], "FixedBuild": "10.0.20348.4200"},
            {"Type": 2, "Description": {"Value": "5077777"}, "ProductID": ["99"], "FixedBuild": "16.0.1"},
        ],
    }],
}

NVD_IOS = {
    "id": "CVE-2026-1111",
    "descriptions": [{"lang": "en", "value": "A vulnerability in the SNMP subsystem of Cisco IOS."}],
    "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 8.6}}]},
    "configurations": [{"nodes": [{"operator": "OR", "cpeMatch": [
        {"vulnerable": True, "criteria": "cpe:2.3:o:cisco:ios:15.2\\(7\\)e8:*:*:*:*:*:*:*"},
    ]}]}],
}
NVD_PHP = {
    "id": "CVE-2026-2222",
    "descriptions": [{"lang": "en", "value": "PHP bug."}],
    "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 7.5}}]},
    "configurations": [{"nodes": [{"operator": "OR", "cpeMatch": [
        {"vulnerable": True, "criteria": "cpe:2.3:a:php:php:*:*:*:*:*:*:*:*",
         "versionStartIncluding": "8.3.0", "versionEndExcluding": "8.3.36"},
    ]}]}],
}
NVD_OTHER = {"id": "CVE-2026-3333", "configurations": [{"nodes": [{"cpeMatch": [
    {"vulnerable": True, "criteria": "cpe:2.3:a:apache:http_server:2.4.1:*:*:*:*:*:*:*"}]}]}]}

OSV = {
    "records": {
        "UBUNTU-CVE-2026-109618": [["CVE-2026-109618"], "critical", 9.8, "PHP out-of-memory corruption"],
        "UBUNTU-CVE-2026-5000": [["CVE-2026-5000"], "high", None, "kernel bug"],
        "RLSA-2026:1": [["CVE-2026-6001", "CVE-2026-6002"], "high", 7.5, "php security update"],
    },
    "releases": {
        "ubuntu:24.04": {
            "php8.3": [["UBUNTU-CVE-2026-109618", "0", "8.3.6-0ubuntu0.24.04.13", None]],
            "linux": [["UBUNTU-CVE-2026-5000", "0", "6.8.0-50.51", None]],
        },
        "rocky:9": {"php-cli": [["RLSA-2026:1", "0", "0:8.0.30-4.el9_6", None]]},
    },
}


def make_feeds(path, **feeds):
    manifest = {"feeds": {}}
    for name, (filename, data) in feeds.items():
        fpath = os.path.join(path, filename)
        if filename.endswith(".gz"):
            with gzip.open(fpath, "wt", encoding="utf-8") as f:
                json.dump(data, f)
        else:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f)
        manifest["feeds"][name] = {"file": filename, "sha256": sha256(fpath), "status": "ok",
                                   "updated": "2099-01-01T00:00:00+00:00"}
    with open(os.path.join(path, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f)
    return FeedStore(str(path))


@pytest.fixture
def store(tmp_path):
    products = {("cisco", "ios"), ("php", "php")}
    nvd = {"updated": None, "cves": {c["id"]: compact_nvd_cve(c, products) for c in (NVD_IOS, NVD_PHP)}}
    assert compact_nvd_cve(NVD_OTHER, products) is None
    return make_feeds(
        tmp_path,
        msrc=("msrc.json.gz", {"docs": {"2026-Oct": compact_cvrf(CVRF, {"Windows Server 2022"})}}),
        nvd=("nvd.json.gz", nvd),
        **{"osv-ubuntu": ("osv-ubuntu.json.gz", OSV), "osv-rocky": ("osv-rocky.json.gz", OSV)},
        kev=("kev.json", {"cves": {"CVE-2026-109618": "2026-10-26"}}),
        epss=("epss.json.gz", {"CVE-2026-109618": [0.91, 0.99]}),
        cisco=("cisco.json", {"ASA|9.8(4)15": [{"advisoryId": "cisco-sa-x", "advisoryTitle": "ASA bug",
                                               "cves": ["CVE-2020-3452"], "cvssBaseScore": "7.5", "sir": "High",
                                               "firstFixed": ["9.8.4.20"], "publicationUrl": "https://example"}]}),
    )


def test_cvrf_keeps_only_wanted_products():
    data = compact_cvrf(CVRF, {"Windows Server 2022"})
    assert set(data) == {"Windows Server 2022", "Windows Server 2022 (Server Core installation)"}
    assert data["Windows Server 2022"][0][:4] == ["CVE-2026-0001", "10.0.20348.4200", "5066666", "critical"]


def test_windows_build_comparison(store):
    old = Facts(build="10.0.20348.4100", install_type="Server")
    [f], notes = store.windows_findings(old)
    assert f.id == "CVE-2026-0001" and f.severity == "critical" and "KB5066666" in f.remediation
    assert store.windows_findings(Facts(build="10.0.20348.4200"))[0] == []
    assert store.windows_findings(Facts(build="10.0.20348.100", install_type="Server Core"))[0]
    assert store.windows_findings(Facts(build="10.0.17763.1"))[0] == []  # 2019 not in this feed


def test_nvd_exact_and_range(store):
    [f] = store.nvd_findings([("cisco", "ios", ["15.2(7)E8"])], "Upgrade IOS")
    assert f.id == "CVE-2026-1111" and f.severity == "high"
    assert not store.nvd_findings([("cisco", "ios", ["15.2(7)E10"])], "x")
    assert [f.id for f in store.nvd_findings([("php", "php", ["8.3.30"])], "x")] == ["CVE-2026-2222"]
    assert not store.nvd_findings([("php", "php", ["8.3.36"])], "x")
    assert not store.nvd_findings([("php", "php", ["8.2.10"])], "x")


def test_linux_deb_source_packages_and_kernel(store):
    facts = Facts(os_id="ubuntu", version="24.04", kernel="6.8.0-45-generic", pkg_records=[
        {"name": "php8.3-cli", "version": "8.3.6-0ubuntu0.24.04.12", "source": "php8.3",
         "source_version": "8.3.6-0ubuntu0.24.04.12"},
        {"name": "linux-image-6.8.0-45-generic", "version": "6.8.0-45.45", "source": "linux", "source_version": "6.8.0-45.45"},
        {"name": "linux-image-6.8.0-40-generic", "version": "6.8.0-40.40", "source": "linux", "source_version": "6.8.0-40.40"},
    ])
    found, notes = store.linux_findings(facts)
    assert {f.id for f in found} == {"CVE-2026-109618", "CVE-2026-5000"}
    php = next(f for f in found if f.id == "CVE-2026-109618")
    assert php.fix_group == "Update package php8.3" and "8.3.6-0ubuntu0.24.04.13" in php.remediation
    facts.pkg_records[0]["source_version"] = "8.3.6-0ubuntu0.24.04.13"
    assert "CVE-2026-109618" not in {f.id for f in store.linux_findings(facts)[0]}


def test_linux_rpm_multi_cve_advisory(store):
    facts = Facts(os_id="rocky", version="9.4", pkg_records=[
        {"name": "php-cli", "version": "0:8.0.30-1.el9_2", "source": "php", "source_version": "0:8.0.30-1.el9_2"}])
    assert {f.id for f in store.linux_findings(facts)[0]} == {"CVE-2026-6001", "CVE-2026-6002"}
    facts.pkg_records[0]["version"] = "8.0.30-4.el9_6"
    assert not store.linux_findings(facts)[0]
    assert store.linux_findings(Facts(os_id="sles", version="15"))[1]  # unsupported distro -> note


def test_cisco_from_feed_folder(store):
    [f] = store.cisco_findings(Facts(os_name="ASA", version="9.8(4)15"))
    assert f.id == "CVE-2020-3452" and "9.8.4.20" in f.remediation
    assert store.cisco_findings(Facts(os_name="ASA", version="9.12(4)")) is None  # not synced yet


def test_kev_epss(store):
    assert "CVE-2026-109618" in store.kev and store.epss["CVE-2026-109618"][0] == 0.91


def test_tampered_feed_is_rejected(tmp_path, store):
    with gzip.open(os.path.join(store.path, "nvd.json.gz"), "wt") as f:
        f.write("{}")
    with pytest.raises(FeedError, match="checksum"):
        FeedStore(store.path)


def test_feed_request_has_no_hosts_and_merges(tmp_path):
    results = [
        DeviceResult(device=Device("10.0.0.1", "linux"), facts=Facts(os_id="ubuntu", version="24.04")),
        DeviceResult(device=Device("10.0.0.2", "windows"), facts=Facts(build="10.0.20348.100")),
        DeviceResult(device=Device("10.0.0.3", "cisco_ios"), facts=Facts(os_name="IOS XE", version="17.06.04")),
    ]
    req = feed_request(results)
    assert req == {"distros": ["ubuntu:24.04"], "windows_products": ["Windows Server 2022"],
                   "cisco_versions": ["IOS XE|17.06.04"], "nvd_products": []}
    assert "10.0.0" not in json.dumps(req)
    req_file = tmp_path / "feed-request.json"
    req_file.write_text(json.dumps(req))
    load_request(str(tmp_path), str(req_file))
    merged = load_request(str(tmp_path), None)  # remembered for the next sync
    assert merged["distros"] == ["ubuntu:24.04"]


def test_unfixed_cves_are_summarised_not_listed(tmp_path):
    osv = {"records": {"U-1": [["CVE-2026-7001"], "high", None, "no fix yet"],
                       "U-2": [["CVE-2026-7002"], "critical", None, "exploited, no fix"]},
           "releases": {"ubuntu:24.04": {"openssl": [["U-1", "0", None, None], ["U-2", "0", None, None]]}}}
    store = make_feeds(tmp_path, **{"osv-ubuntu": ("osv-ubuntu.json.gz", osv)},
                       kev=("kev.json", {"cves": {"CVE-2026-7002": "2026-10-01"}}))
    facts = Facts(os_id="ubuntu", version="24.04", pkg_records=[
        {"name": "libssl3t64", "version": "3.0.13-0ubuntu3.5", "source": "openssl", "source_version": "3.0.13-0ubuntu3.5"},
        {"name": "linux-libc-dev", "version": "6.8.0-1.1", "source": "linux", "source_version": "6.8.0-1.1"}])
    found, notes = store.linux_findings(facts)
    assert [f.id for f in found] == ["CVE-2026-7002"]  # exploited ones are always listed
    assert "1 high/critical CVEs have no Ubuntu fix yet" in notes[0]
    assert {f.id for f in store.linux_findings(facts, include_unfixed=True)[0]} == {"CVE-2026-7001", "CVE-2026-7002"}


def test_rpm_module_streams_are_not_mixed(tmp_path):
    osv = {"records": {"R-base": [["CVE-2026-8001"], "high", 8.1, "base stream fix"],
                       "R-83": [["CVE-2026-8002"], "medium", 5.6, "8.3 module fix"]},
           "releases": {"rocky:9": {"php": [["R-base", "0", "0:8.0.30-8.el9_8.1", None],
                                            ["R-83", "0", "0:8.3.32-1.module+el9.8.0+40268+95fe8e53", None]]}}}
    store = make_feeds(tmp_path, **{"osv-rocky": ("osv-rocky.json.gz", osv)})
    base = Facts(os_id="rocky", version="9.4", pkg_records=[
        {"name": "php-cli", "version": "0:8.0.30-1.el9_2", "source": "php", "source_version": ""}])
    assert [f.id for f in store.linux_findings(base)[0]] == ["CVE-2026-8001"]
    module = Facts(os_id="rocky", version="9.4", pkg_records=[
        {"name": "php-cli", "version": "0:8.3.26-1.module+el9.7.0+40049+21bbec6b", "source": "php", "source_version": ""}])
    assert [f.id for f in store.linux_findings(module)[0]] == ["CVE-2026-8002"]


def test_request_additions_are_normalised_and_validated(tmp_path):
    req = load_request(str(tmp_path), [], {"distros": ["Ubuntu:22.04"], "windows_products": ["2019", "Windows Server 2025"],
                                           "cisco_versions": ["iosxe|17.9.4a", "asa|9.16(4)"]})
    assert req == {"distros": ["ubuntu:22.04"], "windows_products": ["Windows Server 2019", "Windows Server 2025"],
                   "cisco_versions": ["ASA|9.16(4)", "IOS XE|17.9.4a"], "nvd_products": []}
    with pytest.raises(ValueError, match="ubunto"):
        load_request(str(tmp_path), [], {"distros": ["ubunto:24.04"]})
    assert load_request(str(tmp_path))["distros"] == ["ubuntu:22.04"]  # the bad value was not saved


def test_cisco_asa_queries_both_version_formats():
    from unittest import mock

    from vulnscan.feeds import CiscoOpenVuln, asa_spellings

    assert asa_spellings("9.12(4)40") == ["9.12.4.40"] and asa_spellings("8.0(4)") == ["8.0.4"]
    api = CiscoOpenVuln("id", "secret")
    api._token = "token"
    asked = []

    def fake_get(url, params, **kwargs):
        asked.append(params["version"])
        resp = mock.Mock(status_code=200 if params["version"] == "9.12.4.40" else 404)
        resp.json = lambda: {"advisories": [{"advisoryId": "cisco-sa-1"}]}
        return resp

    with mock.patch("vulnscan.feeds.requests.get", fake_get):
        assert [a["advisoryId"] for a in api.advisories("ASA", "9.12(4)40")] == ["cisco-sa-1"]
    assert asked == ["9.12(4)40", "9.12.4.40"]
