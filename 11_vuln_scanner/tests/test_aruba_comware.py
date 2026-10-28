import os
from datetime import date

import pytest

from vulnscan import checks
from vulnscan.collectors import OfflineCollector
from vulnscan.inventory import load_inventory
from vulnscan.models import Device, Facts
from vulnscan.platforms import get_platform

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE = os.path.join(ROOT, "examples", "offline")
RULES = checks.load_json("config_rules.json")


def parse(host, platform):
    p = get_platform(platform)
    out = OfflineCollector(OFFLINE).collect(Device(host=host, platform=platform), p)
    return p, p.parse(out), out


def test_arubaos_controller():
    p, f, out = parse("10.10.0.30", "aruba_os")
    assert (f.model, f.version, f.hostname) == ("Aruba7205", "6.5.4.19", "ctrl-7205-01")
    ids = {x.id for x in checks.run_config_rules("aruba_os", out["config"], RULES)}
    assert {"CFG-AOS-001", "CFG-AOS-002"} <= ids and "CFG-AOS-003" not in ids


def test_arubaos_switch_defaults_are_flagged():
    p, f, out = parse("10.10.0.31", "aruba_switch")
    assert (f.version, f.hostname, f.serial) == ("KB.16.11.0004", "sw-3810-01", "SG00EXAMPLE")
    assert "3810M" in f.model
    assert ("arubanetworks", "arubaos-switch", ["KB.16.11.0004", "16.11.0004"]) in p.nvd_products(f)
    ids = {x.id for x in checks.run_config_rules("aruba_switch", out["config"], RULES)}
    assert {"CFG-AOSS-001", "CFG-AOSS-002", "CFG-AOSS-003"} <= ids and "CFG-AOSS-005" not in ids


def test_aos_cx():
    p, f, _ = parse("10.10.0.32", "aruba_cx")
    assert (f.version, f.hostname) == ("ML.10.13.1010", "sw-cx6200-01") and f.model.startswith("JL724A 6200F")
    assert all(spellings[-1] == "10.13.1010" for _, _, spellings in p.nvd_products(f))


def test_clearpass():
    p, f, _ = parse("10.10.0.33", "clearpass")
    assert (f.version, f.model) == ("6.10.5.185484", "ClearPass C2000")
    assert p.nvd_products(f)[0] == ("arubanetworks", "clearpass_policy_manager", ["6.10.5.185484", "6.10.5"])


def test_manual_appliance_from_inventory(tmp_path):
    inv = tmp_path / "inv.csv"
    inv.write_text("host,name,platform,credential,product,version\n10.0.0.9,sq,manual,,talariax:sendquick,20150606\n")
    [d] = load_inventory(str(inv))
    p = get_platform("manual")
    facts = p.facts_for(d)
    assert p.nvd_products(facts) == [("talariax", "sendquick", ["20150606"])]
    [age] = checks.check_firmware_age(facts)
    assert age.severity == "high" and str(date.today().year - 2015)[:1] in age.title
    assert not checks.check_firmware_age(Facts(version=date.today().strftime("%Y%m%d")))
    bad = tmp_path / "bad.csv"
    bad.write_text("host,platform\n10.0.0.9,manual\n")
    with pytest.raises(ValueError, match="product and version"):
        load_inventory(str(bad))


def test_comware_bulletin_sheet(tmp_path):
    sheet = tmp_path / "comware_rules.csv"
    sheet.write_text(
        "# comment\n"
        "bulletin,cves,title,cvss,severity,series,fixed_release,first_affected,requires_config,url\n"
        "HPESBNW00001,CVE-2099-0001;CVE-2099-0002,SSH flaw,7.5,,5130.*EI,R3507P10,,,https://support.hpe.com/x\n"
        "HPESBNW00001,CVE-2099-0001,SSH flaw,7.5,,5940,R2702P05,,^\\s*ssh server enable,\n")
    rules = checks.load_comware_rules(str(sheet))
    assert rules[0]["affected"] == {"field": "release", "fixed_in": "3507P10"} and rules[0]["cves"] == ["CVE-2099-0001", "CVE-2099-0002"]

    def hits(model, release, config=""):
        f = Facts(model=model, os_name="Comware 7", version="7.1.070", release=release, raw={"config": config})
        return {x.id for x in checks.run_local_advisories("hpe_comware", f, rules)}

    assert hits("5130-48G-PoE+-4SFP+ (370W) EI", "3507P02") == {"CVE-2099-0001"}
    assert not hits("5130-48G-PoE+-4SFP+ (370W) EI", "3507P10")
    assert not hits("5130-48G-PoE+-4SFP+ (370W) HI", "3507P02")  # other series, other rule set
    assert not hits("FlexFabric 5940 48XGT 6QSFP28", "2609", " sysname core\n")  # SSH not enabled
    assert hits("FlexFabric 5940 48XGT 6QSFP28", "2609")  # config not collected: reported, unconfirmed
    assert hits("FlexFabric 5940 48XGT 6QSFP28", "2609", " ssh server enable\n") == {"CVE-2099-0001"}
    assert hits("FlexFabric 5940 48XGT 6QSFP28", "2702P01", " ssh server enable\n")
    assert checks.load_comware_rules(os.path.join(ROOT, "data", "comware_rules.csv")) == []  # template only
