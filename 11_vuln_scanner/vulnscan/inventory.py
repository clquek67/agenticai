"""Load the device inventory, credentials and scan allowlist."""

import csv
import ipaddress
import os
import socket

import yaml

from .models import Device
from .platforms import PLATFORMS


def load_inventory(path):
    """Read a CSV with columns: host, platform, credential[, name, site]."""
    devices = []
    with open(path, newline="", encoding="utf-8") as f:
        for lineno, row in enumerate(csv.DictReader(f), start=2):
            row = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
            host = row.get("host", "")
            if not host or host.startswith("#"):
                continue
            platform = row.get("platform", "")
            if platform not in PLATFORMS:
                raise ValueError(f"{path}:{lineno}: unknown platform '{platform}' (use one of {', '.join(PLATFORMS)})")
            devices.append(
                Device(
                    host=host,
                    platform=platform,
                    credential=row.get("credential", ""),
                    name=row.get("name", ""),
                    site=row.get("site", ""),
                )
            )
    return devices


def load_credentials(path):
    """Read credential profiles. Passwords come from environment variables.

    Each profile: ``username`` plus ``password_env`` (and optional ``secret_env``
    for the enable secret). A literal ``password`` is accepted for lab use only.
    """
    if not path:
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    profiles = {}
    for name, p in (data.get("profiles") or {}).items():
        password = os.environ.get(p["password_env"], "") if p.get("password_env") else p.get("password", "")
        secret = os.environ.get(p["secret_env"], "") if p.get("secret_env") else p.get("secret", "")
        extra = {k: v for k, v in p.items() if k not in ("password", "secret", "password_env", "secret_env")}
        profiles[name] = {**extra, "username": p.get("username", ""), "password": password, "secret": secret}
    return profiles


def load_allowlist(path):
    if not path:
        return None
    nets = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                nets.append(ipaddress.ip_network(line, strict=False))
    return nets


def in_scope(host, allowlist):
    """True if the host (IP or resolvable name) is inside one of the allowed networks."""
    if allowlist is None:
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(host))
        except OSError:
            return False
    return any(ip in net for net in allowlist)
