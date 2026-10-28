import os

from vulnscan import checks
from vulnscan.collectors import OfflineCollector
from vulnscan.models import Device, Facts
from vulnscan.platforms import get_platform, parse_php_blocks

OFFLINE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "offline")
ADVISORIES = checks.load_json("advisories.json")
SOFTWARE_LC = checks.load_json("software_lifecycle.json")
PHP2SHELL = {"CVE-2026-109618", "CVE-2026-109619"}


def facts_for(host, platform):
    p = get_platform(platform)
    return p.parse(OfflineCollector(OFFLINE).collect(Device(host=host, platform=platform), p))


def php(version, build=None, path="C:\\php\\php.exe"):
    return {"name": "php", "version": version, "build": build or version, "sapi": "cli", "path": path, "ini": {}}


def found(platform, facts):
    return {f.id for f in checks.run_software_advisories(platform, facts, ADVISORIES)}


def test_parse_php_blocks():
    text = "### PHP /usr/bin/php8.1\nPHP 8.1.2-1ubuntu2.19 (cli) (built: x) (NTS)\nfile_uploads => On => On\n"
    [inst] = parse_php_blocks(text)
    assert (inst["version"], inst["build"], inst["sapi"]) == ("8.1.2", "8.1.2-1ubuntu2.19", "cli")
    assert inst["ini"] == {"file_uploads": "On"}


def test_php2shell_fixed_versions_per_branch():
    for vulnerable in ("8.5.11", "8.4.26", "8.3.35", "8.2.34", "8.1.31", "7.4.33"):
        assert found("windows", Facts(software=[php(vulnerable)])) == PHP2SHELL, vulnerable
    for fixed in ("8.5.12", "8.4.27", "8.3.36", "8.2.35", "8.4.30"):
        assert not found("windows", Facts(software=[php(fixed)])), fixed


def test_distro_backport_is_respected():
    distro = php("8.3.6", "8.3.6-0ubuntu0.24.04.7", "/usr/bin/php8.3")
    assert found("linux", Facts(software=[distro])) == PHP2SHELL
    assert not found("linux", Facts(software=[distro], fixed_cves=set(PHP2SHELL)))
    # an upstream build (e.g. Remi) is judged on its version even if another package lists the fix
    remi = php("8.4.20", path="/opt/remi/php84/root/usr/bin/php")
    assert found("linux", Facts(software=[remi], packages={"php84-php-cli": "8.4.20"}, fixed_cves=set(PHP2SHELL))) == PHP2SHELL


def test_php_eol_severity_depends_on_source():
    [f] = checks.check_software_lifecycle(Facts(software=[php("8.1.31")]), SOFTWARE_LC)
    assert f.severity == "high"
    distro = Facts(software=[php("8.0.30", path="/usr/bin/php")], packages={"php-cli": "8.0.30-1.el9_2"})
    [f] = checks.check_software_lifecycle(distro, SOFTWARE_LC)
    assert f.severity == "low"
    assert not checks.check_software_lifecycle(Facts(software=[php("8.2.35")]), SOFTWARE_LC)


def test_example_servers():
    ubuntu = facts_for("10.20.1.10", "linux")
    assert ubuntu.model == "Ubuntu 24.04.3 LTS" and ubuntu.hostname == "web-lnx-01"
    assert not found("linux", ubuntu)
    rocky = facts_for("10.20.1.11", "linux")
    assert [s["version"] for s in rocky.software] == ["8.4.20", "8.0.30"]
    assert found("linux", rocky) == PHP2SHELL
    win = facts_for("10.20.1.20", "windows")
    assert win.hostname == "WEB-WIN-01" and len(win.software) == 3
    [finding, _] = checks.run_software_advisories("windows", win, ADVISORIES)
    assert not any("php82" in e for e in finding.evidence)  # 8.2.35 is patched
