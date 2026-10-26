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
    netmiko_type = ""
    # key -> command. Keys "version" and "config" are used by the checks.
    commands = {}

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


PLATFORMS = {p.name: p for p in (CiscoIOS(), CiscoASA(), HPEComware())}


def get_platform(name):
    try:
        return PLATFORMS[name]
    except KeyError:
        raise ValueError(f"Unknown platform '{name}'. Supported: {', '.join(PLATFORMS)}") from None
