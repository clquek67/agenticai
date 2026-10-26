"""VulnScan command line.

Live scan (SSH to every device in the inventory):
    python scan.py --inventory devices.csv --credentials credentials.yaml --allowlist allowlist.txt

Offline demo (no devices needed):
    python scan.py --inventory examples/devices.csv --offline examples/offline --no-network
"""

import argparse
import logging
import os
import sys

from vulnscan.checks import DATA_DIR
from vulnscan.collectors import OfflineCollector, SSHCollector
from vulnscan.feeds import CiscoOpenVuln, KEVCatalog
from vulnscan.inventory import load_allowlist, load_credentials, load_inventory
from vulnscan.report import write_all
from vulnscan.scanner import Scanner, default_report_dir


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Credentialed, read-only vulnerability scanner for network devices.")
    p.add_argument("--inventory", required=True, help="CSV with host, platform, credential[, name, site]")
    p.add_argument("--credentials", help="YAML credential profiles (passwords from environment variables)")
    p.add_argument("--allowlist", help="file of CIDRs that may be scanned; hosts outside are skipped")
    p.add_argument("--offline", metavar="DIR", help="read saved command output from DIR instead of SSH")
    p.add_argument("--out", help="output folder (default: reports/scan-<timestamp>)")
    p.add_argument("--workers", type=int, default=5, help="devices scanned in parallel (default 5: gentle)")
    p.add_argument("--timeout", type=int, default=30, help="SSH timeout in seconds")
    p.add_argument("--no-network", action="store_true", help="don't download feeds or call vendor APIs")
    p.add_argument("--title", default="Vulnerability Assessment Report")
    p.add_argument("--org", default="", help="organisation name shown on the report")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(message)s")

    devices = load_inventory(args.inventory)
    if not devices:
        sys.exit("The inventory has no devices.")
    allowlist = load_allowlist(args.allowlist)

    if args.offline:
        collector = OfflineCollector(args.offline)
    else:
        if not args.credentials:
            sys.exit("--credentials is required for a live scan (or use --offline DIR).")
        if allowlist is None:
            sys.exit("--allowlist is required for a live scan, so only approved networks are touched.")
        collector = SSHCollector(load_credentials(args.credentials), timeout=args.timeout)

    kev = KEVCatalog.load(offline=args.no_network, snapshot_path=os.path.join(DATA_DIR, "kev_snapshot.json"))
    cisco_api = None
    cid, secret = os.environ.get("CISCO_CLIENT_ID"), os.environ.get("CISCO_CLIENT_SECRET")
    if cid and secret and not args.no_network:
        cisco_api = CiscoOpenVuln(cid, secret)

    scanner = Scanner(collector, kev, cisco_api=cisco_api, allowlist=allowlist, workers=args.workers)
    print(f"Scanning {len(devices)} devices ({'offline' if args.offline else 'live SSH'}, {args.workers} at a time)...")
    result = scanner.scan(devices)

    paths = write_all(result, args.out or default_report_dir(), title=args.title, org=args.org)
    counts = result.severity_counts()
    print(f"Scanned {len(result.scanned)}/{len(result.results)} devices · risk {result.risk_score()}/100 · "
          f"critical {counts['critical']} · high {counts['high']} · medium {counts['medium']} · "
          f"actively exploited {result.kev_count()}")
    for r in result.not_scanned:
        print(f"  not scanned: {r.device.label} ({r.status}: {r.error})")
    print(f"Report: {paths['html']}\nData:   {paths['json']}, {paths['csv']}")


if __name__ == "__main__":
    main()
