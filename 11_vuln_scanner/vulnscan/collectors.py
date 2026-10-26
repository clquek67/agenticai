"""Collect command output from devices: live over SSH, or from saved files."""

import os
import re


class CollectionError(Exception):
    pass


class OfflineCollector:
    """Reads ``<dir>/<host or name>/<key>.txt``, e.g. ``offline/10.10.0.1/version.txt``.

    Useful for testing, and for scanning output exported by another tool.
    """

    def __init__(self, directory):
        self.directory = directory

    def collect(self, device, platform):
        for folder in (device.host, device.name):
            path = os.path.join(self.directory, folder) if folder else ""
            if path and os.path.isdir(path):
                break
        else:
            raise CollectionError(f"no saved output found for {device.label}")
        outputs = {}
        for key in platform.commands:
            fpath = os.path.join(path, f"{key}.txt")
            if os.path.exists(fpath):
                with open(fpath, encoding="utf-8", errors="replace") as f:
                    outputs[key] = f.read()
        if "version" not in outputs:
            raise CollectionError(f"{path}/version.txt is missing")
        return outputs


# Only show/display commands are ever sent. This guard stops a bad platform
# definition from sending anything that could change a device.
_READ_ONLY = re.compile(r"^(show|display)\s")


class SSHCollector:
    """Logs in with Netmiko and runs the platform's read-only commands."""

    def __init__(self, credentials, timeout=30):
        self.credentials = credentials
        self.timeout = timeout

    def collect(self, device, platform):
        from netmiko import ConnectHandler  # imported lazily so offline mode needs no netmiko

        cred = self.credentials.get(device.credential)
        if not cred or not cred["username"]:
            raise CollectionError(f"credential profile '{device.credential}' not found or has no username")
        if not cred["password"]:
            raise CollectionError(f"credential profile '{device.credential}' has no password (is the env var set?)")
        params = {
            "device_type": platform.netmiko_type,
            "host": device.host,
            "username": cred["username"],
            "password": cred["password"],
            "secret": cred["secret"],
            "timeout": self.timeout,
            "conn_timeout": self.timeout,
            "fast_cli": False,
        }
        outputs = {}
        try:
            with ConnectHandler(**params) as conn:
                if cred["secret"] and platform.name.startswith("cisco"):
                    conn.enable()
                for key, command in platform.commands.items():
                    if not _READ_ONLY.match(command):
                        raise CollectionError(f"refusing non read-only command: {command}")
                    outputs[key] = conn.send_command(command, read_timeout=120)
        except CollectionError:
            raise
        except Exception as exc:  # Netmiko raises many types; report them all the same way
            first_line = (str(exc).strip().splitlines() or [""])[0]
            raise CollectionError(f"{type(exc).__name__}: {first_line}") from exc
        return outputs
