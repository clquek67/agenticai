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
        first = next(iter(platform.commands))
        if first not in outputs:
            raise CollectionError(f"{path}/{first}.txt is missing")
        return outputs


class SSHCollector:
    """Logs in and runs the platform's read-only commands: Netmiko over SSH, or WinRM for Windows."""

    def __init__(self, credentials, timeout=30):
        self.credentials = credentials
        self.timeout = timeout

    def collect(self, device, platform):
        cred = self.credentials.get(device.credential)
        if not cred or not cred["username"]:
            raise CollectionError(f"credential profile '{device.credential}' not found or has no username")
        if not cred["password"]:
            raise CollectionError(f"credential profile '{device.credential}' has no password (is the env var set?)")
        if platform.transport == "winrm":
            return self._collect_winrm(device, platform, cred)
        return self._collect_ssh(device, platform, cred)

    def _collect_ssh(self, device, platform, cred):
        from netmiko import ConnectHandler  # imported lazily so offline mode needs no netmiko
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
                    # On network devices only show/display commands are ever sent. This
                    # guard stops a bad platform definition from changing a device.
                    if platform.read_only_pattern and not re.match(platform.read_only_pattern, command):
                        raise CollectionError(f"refusing non read-only command: {command}")
                    outputs[key] = conn.send_command(command, read_timeout=120)
        except CollectionError:
            raise
        except Exception as exc:  # Netmiko raises many types; report them all the same way
            first_line = (str(exc).strip().splitlines() or [""])[0]
            raise CollectionError(f"{type(exc).__name__}: {first_line}") from exc
        return outputs

    def _collect_winrm(self, device, platform, cred):
        import winrm  # pywinrm, imported lazily

        port = cred.get("winrm_port", 5986)
        scheme = "https" if cred.get("winrm_https", True) else "http"
        session = winrm.Session(
            f"{scheme}://{device.host}:{port}/wsman",
            auth=(cred["username"], cred["password"]),
            transport=cred.get("winrm_transport", "ntlm"),
            server_cert_validation="validate" if cred.get("verify_tls", True) else "ignore",
            read_timeout_sec=max(self.timeout, 30) + 10,
            operation_timeout_sec=max(self.timeout, 30),
        )
        outputs = {}
        try:
            for key, script in platform.commands.items():
                r = session.run_ps(script)
                outputs[key] = r.std_out.decode("utf-8", errors="replace")
                if r.status_code != 0 and not outputs[key].strip():
                    raise CollectionError(f"PowerShell exited {r.status_code}: {r.std_err.decode(errors='replace')[:200]}")
        except CollectionError:
            raise
        except Exception as exc:
            first_line = (str(exc).strip().splitlines() or [""])[0]
            raise CollectionError(f"{type(exc).__name__}: {first_line}") from exc
        return outputs
