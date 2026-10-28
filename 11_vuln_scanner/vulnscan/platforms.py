"""Per-platform knowledge: which read-only commands to run and how to parse them.

To add a vendor, subclass ``Platform``, set its commands and Netmiko device
type, implement ``parse`` and register it in ``PLATFORMS``.
"""

import re

from .models import Facts
from .versions import normalize_dotted


def _search(pattern, text, group=1, flags=re.MULTILINE):
    m = re.search(pattern, text or "", flags)
    return m.group(group).strip() if m else ""


class Platform:
    name = ""
    label = ""
    transport = "ssh"  # "ssh" (Netmiko) or "winrm"
    netmiko_type = ""
    # key -> command. Keys "version" and "config" are used by the checks.
    commands = {}
    # Every command must match this before it is sent. None means the commands
    # are fixed scripts in this file that only read information.
    read_only_pattern = r"^(show|display)\s"

    def parse(self, outputs):
        raise NotImplementedError

    def nvd_products(self, facts):
        """[(vendor, product, [version spellings])] used to look the device up in NVD."""
        return []


class CiscoIOS(Platform):
    """Cisco IOS and IOS XE routers and switches (2811, 2960X, 3750G, ISR 4331, ...)."""

    name = "cisco_ios"
    label = "Cisco IOS / IOS XE"
    netmiko_type = "cisco_ios"
    commands = {"version": "show version", "config": "show running-config"}

    def parse(self, outputs):
        ver = outputs.get("version", "")
        cfg = outputs.get("config", "")
        is_xe = bool(re.search(r"IOS[ -]XE", ver))
        version = _search(r"Cisco IOS XE Software, Version\s+(\S+)", ver) or _search(
            r"Cisco IOS Software.*?Version\s+([^\s,]+)", ver
        )
        model = (
            _search(r"^Model [Nn]umber\s*:\s*(\S+)", ver)
            or _search(r"^[Cc]isco\s+(\S+)\s+\(.*?\)\s+(?:processor|with)", ver)
        )
        return Facts(
            hostname=_search(r"^hostname\s+(\S+)", cfg) or _search(r"^(\S+)\s+uptime is", ver),
            model=model,
            os_name="IOS XE" if is_xe else "IOS",
            version=version,
            serial=_search(r"^(?:System [Ss]erial [Nn]umber\s*:|Processor board ID)\s*(\S+)", ver),
        )

    def nvd_products(self, facts):
        if facts.os_name == "IOS XE":
            return [("cisco", "ios_xe", [normalize_dotted(facts.version), facts.version])]
        return [("cisco", "ios", [facts.version])]


class CiscoASA(Platform):
    """Cisco ASA firewalls (5512-X, 5520, 5525-X, ...)."""

    name = "cisco_asa"
    label = "Cisco ASA"
    netmiko_type = "cisco_asa"
    commands = {"version": "show version", "config": "show running-config"}

    def parse(self, outputs):
        ver = outputs.get("version", "")
        cfg = outputs.get("config", "")
        return Facts(
            hostname=_search(r"^hostname\s+(\S+)", cfg) or _search(r"^(\S+)\s+up\s+\d", ver),
            model=_search(r"^Hardware:\s+([^,\s]+)", ver),
            os_name="ASA",
            version=_search(r"Adaptive Security Appliance Software Version\s+(\S+)", ver),
            serial=_search(r"^Serial Number:\s*(\S+)", ver),
        )

    def nvd_products(self, facts):
        dotted = re.sub(r"[()]", ".", facts.version).replace("..", ".").strip(".")
        return [("cisco", "adaptive_security_appliance_software", [facts.version, dotted])]


class HPEComware(Platform):
    """HPE / H3C Comware 5 and 7 switches (5130, 5500, A5500, 5510, 5900, 5700, 5940, HP 850)."""

    name = "hpe_comware"
    label = "HPE Comware"
    netmiko_type = "hp_comware"
    commands = {"version": "display version", "config": "display current-configuration"}

    def parse(self, outputs):
        ver = outputs.get("version", "")
        cfg = outputs.get("config", "")
        # "HPE 5130-48G-PoE+-4SFP+ (370W) EI Switch uptime is ..." or
        # "HP A5500-24G-4SFP HI Switch with 2 Interface Slots uptime is ..."
        model = _search(r"^(?:HPE?|H3C)\s+(.+?)\s+Switch\b.*uptime is", ver) or _search(
            r"^(?:HPE?|H3C)\s+(.+?)\s+uptime is", ver
        )
        return Facts(
            hostname=_search(r"^\s*sysname\s+(\S+)", cfg),
            model=model,
            os_name="Comware " + _search(r"Comware Software, Version\s+(\d+)", ver),
            version=_search(r"Comware Software, Version\s+([\d.]+)", ver),
            release=_search(r"Comware Software, Version\s+[\d.]+,\s*Release\s+(\S+)", ver),
            serial=_search(r"DEVICE_SERIAL_NUMBER\s*:\s*(\S+)", ver),
        )

    def nvd_products(self, facts):
        # NVD's Comware data is sparse; this catches the CVEs that do list Comware versions.
        spellings = [facts.release, f"r{facts.release}", f"{facts.version}_r{facts.release}", facts.version]
        return [(v, "comware", spellings) for v in ("h3c", "hp", "hpe")]



# --- HPE Aruba ------------------------------------------------------------------

def _hostname(cfg):
    return _search(r'^hostname\s+"?([^"\n]+?)"?\s*$', cfg)


class ArubaOS(Platform):
    """HPE Aruba mobility controllers running ArubaOS 6.x / 8.x (7205, 7210, 7240, ...)."""

    name = "aruba_os"
    label = "HPE Aruba ArubaOS controller"
    netmiko_type = "aruba_os"
    commands = {"version": "show version", "config": "show running-config"}

    def parse(self, outputs):
        ver = outputs.get("version", "")
        return Facts(
            hostname=_hostname(outputs.get("config", "")),
            model=_search(r"ArubaOS \(MODEL:\s*([^)]+)\)", ver),
            os_name="ArubaOS",
            version=_search(r"ArubaOS \(MODEL:[^)]*\),\s*Version\s+(\S+)", ver),
        )

    def nvd_products(self, facts):
        return [("arubanetworks", "arubaos", [facts.version]), ("hpe", "arubaos", [facts.version])]


class ArubaOSSwitch(Platform):
    """HPE Aruba switches running ArubaOS-Switch / ProVision (2930, 3810M, 5400R: KB., WC., YA. ...)."""

    name = "aruba_switch"
    label = "HPE Aruba ArubaOS-Switch"
    netmiko_type = "aruba_osswitch"
    commands = {"version": "show version", "modules": "show modules", "config": "show running-config"}

    def parse(self, outputs):
        ver = outputs.get("version", "")
        mods = outputs.get("modules", "")
        return Facts(
            hostname=_hostname(outputs.get("config", "")),
            model=_search(r"Chassis:\s*(.+?)\s{2,}", mods) or _search(r"Chassis:\s*(.+?)\s*Serial", mods),
            os_name="ArubaOS-Switch",
            version=_search(r"^\s*([A-Z]{1,3}\.\d{2}\.\d{2}\.\d{4})\s*$", ver),
            serial=_search(r"Serial Number:\s*(\S+)", mods),
        )

    def nvd_products(self, facts):
        bare = re.sub(r"^[A-Z]+\.", "", facts.version)  # KB.16.11.0004 -> 16.11.0004
        spellings = [facts.version, bare]
        return [(v, "arubaos-switch", spellings) for v in ("arubanetworks", "hpe", "hp")]


class ArubaCX(Platform):
    """HPE Aruba switches running AOS-CX (4100i, 6000, 6100, 6200, 6300, 8100, 8320, 8360, ...)."""

    name = "aruba_cx"
    label = "HPE Aruba AOS-CX"
    netmiko_type = "aruba_aoscx"
    commands = {"version": "show version", "system": "show system", "config": "show running-config"}

    def parse(self, outputs):
        ver, system = outputs.get("version", ""), outputs.get("system", "")
        return Facts(
            hostname=_hostname(outputs.get("config", "")) or _search(r"^Hostname\s*:\s*(\S+)", system),
            model=_search(r"^Product Name\s*:\s*(.+?)\s*$", system),
            os_name="AOS-CX",
            version=_search(r"^Version\s*:\s*(\S+)", ver),
            serial=_search(r"^Chassis Serial Nbr\s*:\s*(\S+)", system),
        )

    def nvd_products(self, facts):
        bare = re.sub(r"^[A-Z]+\.", "", facts.version)  # FL.10.13.1000 -> 10.13.1000
        spellings = [facts.version, bare]
        return [(v, p, spellings) for v in ("arubanetworks", "hpe") for p in ("arubaos-cx", "aos-cx")]


class ClearPass(Platform):
    """HPE Aruba ClearPass Policy Manager (appadmin CLI)."""

    name = "clearpass"
    label = "HPE Aruba ClearPass"
    netmiko_type = "generic"
    commands = {"version": "show version"}

    def parse(self, outputs):
        ver = outputs.get("version", "")
        return Facts(
            model="ClearPass " + _search(r"model number\s*:?\s*(\S+)", ver, flags=re.IGNORECASE | re.MULTILINE),
            os_name="ClearPass",
            version=_search(r"software version\s*:?\s*(\d+\.\d+\.\d+(?:\.\d+)?)", ver, flags=re.IGNORECASE),
        )

    def nvd_products(self, facts):
        short = ".".join(facts.version.split(".")[:3])  # 6.10.5.185484 -> 6.10.5 (NVD's spelling)
        return [(v, "clearpass_policy_manager", [facts.version, short]) for v in ("arubanetworks", "hpe")]


# --- appliances without a supported login ----------------------------------------

class ManualAppliance(Platform):
    """Devices the scanner can't log in to (SendQuick, TippingPoint, ...). The inventory gives the
    product and version; they are checked against NVD and reported as unverified."""

    name = "manual"
    label = "Appliance (version from inventory)"
    transport = "none"
    commands = {}

    def facts_for(self, device):
        return Facts(model=device.product, os_name="manual", version=device.version)

    def parse(self, outputs):
        return Facts()

    def nvd_products(self, facts):
        products = []
        for vp in (facts.model or "").split(";"):
            vendor, _, product = vp.strip().partition(":")
            if vendor and product:
                products.append((vendor, product, [facts.version]))
        return products


# --- servers -------------------------------------------------------------------

_INI_KEYS = "session.upload_progress.enabled|file_uploads|memory_limit|post_max_size|expose_php"
_PHP_LINE = re.compile(r"^PHP (\d+\.\d+\.\d+)(\S*) \(([^)]+)\)", re.MULTILINE)


def parse_php_blocks(text):
    """Parse '### PHP <path>' blocks: a ``php -v`` line plus optional ``php -i`` ini lines."""
    installs = []
    for block in re.split(r"^### PHP ", text or "", flags=re.MULTILINE)[1:]:
        path, _, body = block.partition("\n")
        m = _PHP_LINE.search(body)
        if not m:
            continue
        ini = {}
        for line in body.splitlines():
            parts = [x.strip() for x in line.split("=>")]
            if len(parts) == 3 and re.fullmatch(_INI_KEYS, parts[0]):
                ini[parts[0]] = parts[1]  # local value
        installs.append({
            "name": "php", "version": m.group(1), "build": m.group(1) + m.group(2),
            "sapi": m.group(3), "path": path.strip(), "ini": ini,
        })
    return installs


class LinuxServer(Platform):
    """Linux servers (Ubuntu, Debian, RHEL, Rocky, Alma, ...). Finds PHP installs and package fixes."""

    name = "linux"
    label = "Linux server"
    netmiko_type = "linux"
    read_only_pattern = None
    _bins = ("/usr/bin/php /usr/bin/php[0-9]* /usr/local/bin/php /opt/remi/*/root/usr/bin/php "
             "/opt/plesk/php/*/bin/php /opt/cpanel/ea-php*/root/usr/bin/php")
    commands = {
        "os": "cat /etc/os-release; echo HOSTNAME=$(uname -n); echo KERNEL=$(uname -r)",
        "php": (
            f"for p in $(for x in {_bins}; do [ -x \"$x\" ] && readlink -f \"$x\"; done | sort -u); do "
            "echo \"### PHP $p\"; \"$p\" -v 2>/dev/null | head -1; "
            f"\"$p\" -i 2>/dev/null | grep -E '^({_INI_KEYS}) '; done"
        ),
        # Every installed package: deb|name|version|source|source version, or rpm|name|epoch:version-release|source rpm
        "packages": (
            "dpkg-query -W -f='${db:Status-Abbrev}|${Package}|${Version}|${source:Package}|${source:Version}\\n' "
            "2>/dev/null | grep '^ii' | sed 's/^ii */deb/'; "
            "rpm -qa --qf 'rpm|%{NAME}|%{EPOCHNUM}:%{VERSION}-%{RELEASE}|%{SOURCERPM}\\n' 2>/dev/null; true"
        ),
        # Distro packages list the CVEs they fix in their changelogs (backports keep the old version number).
        "fixed_cves": (
            "(for f in /usr/share/doc/php*/changelog.Debian.gz; do zcat \"$f\" 2>/dev/null; done; "
            "rpm -qa 'php*' 2>/dev/null | xargs -r rpm -q --changelog 2>/dev/null) "
            "| grep -oE 'CVE-[0-9]{4}-[0-9]+' | sort -u"
        ),
        "processes": "ps -eo comm= | sort -u | grep -E '^(php|apache2|httpd|nginx|lsphp|litespeed|frankenphp)' ; true",
    }

    def parse(self, outputs):
        osr = outputs.get("os", "")
        records = parse_packages(outputs.get("packages", ""))
        return Facts(
            hostname=_search(r"^HOSTNAME=(\S+)", osr),
            model=_search(r'^PRETTY_NAME="?([^"\n]+)"?', osr),
            os_name="Linux",
            os_id=_search(r'^ID="?([^"\n]+)"?', osr).lower(),
            version=_search(r'^VERSION_ID="?([^"\n]+)"?', osr),
            kernel=_search(r"^KERNEL=(\S+)", osr),
            software=parse_php_blocks(outputs.get("php", "")),
            packages={r["name"]: r["version"] for r in records if r["name"].startswith("php")},
            pkg_records=records,
            fixed_cves=set(re.findall(r"CVE-\d{4}-\d+", outputs.get("fixed_cves", ""))),
        )


def parse_packages(text):
    records = []
    for line in (text or "").splitlines():
        parts = line.strip().split("|")
        if parts[0] == "deb" and len(parts) == 5:
            _, name, version, source, source_version = parts
            name = name.split(":")[0]  # drop :amd64
            records.append({"name": name, "version": version, "source": source or name,
                            "source_version": source_version or version})
        elif parts[0] == "rpm" and len(parts) == 4:
            _, name, version, srpm = parts
            if name == "gpg-pubkey":
                continue
            source = re.sub(r"-[^-]+-[^-]+\.src\.rpm$", "", srpm) if srpm.endswith(".src.rpm") else ""
            records.append({"name": name, "version": version, "source": source, "source_version": version})
        elif len(parts) == 1 and len(line.split()) == 2:  # older "name version" format
            name, version = line.split()
            records.append({"name": name, "version": version, "source": name, "source_version": version})
    return records


_WINDOWS_SCRIPT = r"""
$ErrorActionPreference = 'SilentlyContinue'
$os = Get-CimInstance Win32_OperatingSystem
"OS=$($os.Caption)"; "OSVERSION=$($os.Version)"; "HOSTNAME=$($os.CSName)"
$cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
"BUILD=10.0.$($cv.CurrentBuild).$($cv.UBR)"; "INSTALLTYPE=$($cv.InstallationType)"
$paths = @()
Get-Command php.exe -All | ForEach-Object { $paths += $_.Source }
$cfg = "$env:windir\system32\inetsrv\config\applicationHost.config"
if (Test-Path $cfg) { ([xml](Get-Content $cfg -Raw)).configuration.'system.webServer'.fastCgi.application | ForEach-Object { $paths += $_.fullPath } }
foreach ($d in 'C:\php', 'C:\Program Files\PHP', 'C:\Program Files (x86)\PHP', 'C:\xampp\php', 'C:\wamp64\bin\php', 'C:\Program Files\iis express\PHP') {
  if (Test-Path $d) { Get-ChildItem $d -Recurse -Depth 2 -Include php.exe, php-cgi.exe | ForEach-Object { $paths += $_.FullName } }
}
$paths = $paths | Where-Object { $_ } | ForEach-Object { [Environment]::ExpandEnvironmentVariables($_) } | Sort-Object -Unique
foreach ($p in $paths) {
  if (-not (Test-Path $p)) { continue }
  "### PHP $p"
  & $p -v 2>$null | Select-Object -First 1
  $cli = Join-Path (Split-Path $p) 'php.exe'
  if (Test-Path $cli) { & $cli -i 2>$null | Select-String -Pattern '^(session.upload_progress.enabled|file_uploads|memory_limit|post_max_size|expose_php) ' | ForEach-Object { $_.Line } }
}
"""


class WindowsServer(Platform):
    """Windows servers over WinRM. Finds PHP on PATH, in IIS FastCGI and in common folders."""

    name = "windows"
    label = "Windows server"
    transport = "winrm"
    read_only_pattern = None
    commands = {"inventory": _WINDOWS_SCRIPT}

    def parse(self, outputs):
        text = (outputs.get("inventory", "") or "").replace("\r\n", "\n")
        return Facts(
            hostname=_search(r"^HOSTNAME=(.+)$", text),
            model=_search(r"^OS=(.+)$", text),
            os_name="Windows",
            version=_search(r"^OSVERSION=(.+)$", text),
            build=_search(r"^BUILD=(10\.0\.\d+\.\d+)\s*$", text),
            install_type=_search(r"^INSTALLTYPE=(.+)$", text),
            software=parse_php_blocks(text),
        )


PLATFORMS = {p.name: p for p in (CiscoIOS(), CiscoASA(), HPEComware(), ArubaOS(), ArubaOSSwitch(), ArubaCX(),
                                  ClearPass(), LinuxServer(), WindowsServer(), ManualAppliance())}


def get_platform(name):
    try:
        return PLATFORMS[name]
    except KeyError:
        raise ValueError(f"Unknown platform '{name}'. Supported: {', '.join(PLATFORMS)}") from None
