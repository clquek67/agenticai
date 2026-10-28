"""Per-platform knowledge: which read-only commands to run and how to parse them.

To add a vendor, subclass ``Platform``, set its commands and Netmiko device
type, implement ``parse`` and register it in ``PLATFORMS``.
"""

import re

from .models import Facts


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
        "os": "cat /etc/os-release; echo HOSTNAME=$(uname -n)",
        "php": (
            f"for p in $(for x in {_bins}; do [ -x \"$x\" ] && readlink -f \"$x\"; done | sort -u); do "
            "echo \"### PHP $p\"; \"$p\" -v 2>/dev/null | head -1; "
            f"\"$p\" -i 2>/dev/null | grep -E '^({_INI_KEYS}) '; done"
        ),
        "packages": (
            "dpkg-query -W -f='${Package} ${Version}\\n' 'php*' 2>/dev/null; "
            "rpm -qa --qf '%{NAME} %{VERSION}-%{RELEASE}\\n' 'php*' 2>/dev/null; true"
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
        packages = {}
        for line in outputs.get("packages", "").splitlines():
            parts = line.split()
            if len(parts) == 2:
                packages[parts[0]] = parts[1]
        return Facts(
            hostname=_search(r"^HOSTNAME=(\S+)", osr),
            model=_search(r'^PRETTY_NAME="?([^"\n]+)"?', osr),
            os_name="Linux",
            version=_search(r'^VERSION_ID="?([^"\n]+)"?', osr),
            software=parse_php_blocks(outputs.get("php", "")),
            packages=packages,
            fixed_cves=set(re.findall(r"CVE-\d{4}-\d+", outputs.get("fixed_cves", ""))),
        )


_WINDOWS_SCRIPT = r"""
$ErrorActionPreference = 'SilentlyContinue'
$os = Get-CimInstance Win32_OperatingSystem
"OS=$($os.Caption)"; "OSVERSION=$($os.Version)"; "HOSTNAME=$($os.CSName)"
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
            software=parse_php_blocks(text),
        )


PLATFORMS = {p.name: p for p in (CiscoIOS(), CiscoASA(), HPEComware(), LinuxServer(), WindowsServer())}


def get_platform(name):
    try:
        return PLATFORMS[name]
    except KeyError:
        raise ValueError(f"Unknown platform '{name}'. Supported: {', '.join(PLATFORMS)}") from None
