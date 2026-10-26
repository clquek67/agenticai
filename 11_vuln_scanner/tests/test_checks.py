from vulnscan import checks
from vulnscan.models import Facts

ADVISORIES = checks.load_json("advisories.json")
RULES = checks.load_json("config_rules.json")
LIFECYCLE = checks.load_json("lifecycle.json")


def ids(findings):
    return {f.id for f in findings}


def xe(version, config="ip http server\n"):
    return Facts(model="ISR4331/K9", os_name="IOS XE", version=version, raw={"config": config})


def test_webui_cve_needs_vulnerable_version_and_enabled_feature():
    assert "CVE-2023-20198" in ids(checks.run_local_advisories("cisco_ios", xe("17.06.04"), ADVISORIES))
    # fixed release on the same train
    assert "CVE-2023-20198" not in ids(checks.run_local_advisories("cisco_ios", xe("17.6.6a"), ADVISORIES))
    # vulnerable version but web UI disabled
    assert "CVE-2023-20198" not in ids(checks.run_local_advisories("cisco_ios", xe("17.06.04", "no ip http server\n"), ADVISORIES))
    # classic IOS is not IOS XE
    ios = Facts(os_name="IOS", version="15.2(7)E8", raw={"config": "ip http server\n"})
    assert not checks.run_local_advisories("cisco_ios", ios, ADVISORIES)


def test_asa_upper_bound():
    asa = lambda v: Facts(os_name="ASA", version=v, raw={"config": "webvpn\n enable outside\n"})
    assert "CVE-2020-3452" in ids(checks.run_local_advisories("cisco_asa", asa("9.8(4)15"), ADVISORIES))
    assert "CVE-2020-3452" not in ids(checks.run_local_advisories("cisco_asa", asa("9.8(4)20"), ADVISORIES))
    assert "CVE-2020-3452" not in ids(checks.run_local_advisories("cisco_asa", asa("9.16(4)"), ADVISORIES))


def test_config_rules_present_and_absent():
    cfg = "hostname x\nsnmp-server community public RO\nline vty 0 4\n transport input telnet ssh\n"
    found = ids(checks.run_config_rules("cisco_ios", cfg, RULES))
    assert {"CFG-IOS-001", "CFG-IOS-003", "CFG-IOS-008"} <= found
    assert "CFG-IOS-005" not in found


def test_evidence_is_redacted():
    cfg = "local-user admin\n password simple SuperSecret1\n snmp-agent community read simple corpRO\n"
    findings = checks.run_config_rules("hpe_comware", cfg, RULES)
    text = " ".join(e for f in findings for e in f.evidence)
    assert "SuperSecret1" not in text and "corpRO" not in text


def test_lifecycle():
    status, finding = checks.check_lifecycle(Facts(model="2811"), LIFECYCLE)
    assert status == "end_of_support" and finding.severity == "high"
    assert checks.check_lifecycle(Facts(model="WS-C2960X-24TS-L"), LIFECYCLE)[0] == "end_of_sale"
    assert checks.check_lifecycle(Facts(model="5130-48G-PoE+-4SFP+ (370W) EI"), LIFECYCLE) == ("unknown", None)
