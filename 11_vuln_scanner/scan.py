"""VulnScan command line.

Offline scanner with downloaded feeds (two-machine setup):
    # on the internet-connected sync machine
    python scan.py --sync-feeds --out feeds [--request feed-request.json]
    # copy the feeds folder to the scanner, then
    python scan.py --inventory devices.csv --credentials credentials.yaml --allowlist allowlist.txt --feeds feeds

Live scan with direct internet access instead of feeds:
    python scan.py --inventory devices.csv --credentials credentials.yaml --allowlist allowlist.txt

Offline demo (no devices needed):
    python scan.py --inventory examples/devices.csv --offline examples/offline --feeds examples/feeds
"""

import argparse
import json
import logging
import os
import sys

from vulnscan.checks import DATA_DIR
from vulnscan.collectors import OfflineCollector, SSHCollector
from vulnscan.feeds import CiscoOpenVuln, KEVCatalog
from vulnscan.feedstore import FeedError, FeedStore, feed_request
from vulnscan.inventory import load_allowlist, load_credentials, load_inventory
from vulnscan.report import write_all
from vulnscan.scanner import Scanner, default_report_dir


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Credentialed, read-only vulnerability scanner for network devices and servers.")
    p.add_argument("--inventory", help="CSV with host, platform, credential[, name, site]")
    p.add_argument("--credentials", help="YAML credential profiles (passwords from environment variables)")
    p.add_argument("--allowlist", help="file of CIDRs that may be scanned; hosts outside are skipped")
    p.add_argument("--offline", metavar="DIR", help="read saved command output from DIR instead of logging in")
    p.add_argument("--feeds", metavar="DIR", help="use vulnerability feeds downloaded with --sync-feeds (no internet needed)")
    p.add_argument("--out", help="output folder (scan default: reports/scan-<timestamp>; sync default: feeds)")
    p.add_argument("--include-unfixed", action="store_true",
                   help="also list high/critical Linux CVEs the distribution has not fixed yet")
    p.add_argument("--workers", type=int, default=5, help="devices scanned in parallel (default 5: gentle)")
    p.add_argument("--timeout", type=int, default=30, help="SSH/WinRM timeout in seconds")
    p.add_argument("--no-network", action="store_true", help="don't download feeds or call vendor APIs")
    p.add_argument("--title", default="Vulnerability Assessment Report")
    p.add_argument("--org", default="", help="organisation name shown on the report")
    p.add_argument("-v", "--verbose", action="store_true")
    sync = p.add_argument_group("sync machine (internet access)")
    sync.add_argument("--sync-feeds", action="store_true", help="download/refresh the vulnerability feeds into --out")
    sync.add_argument("--request", nargs="+", default=[],
                      help="one or more feed-request.json files written by scans (e.g. one per site)")
    sync.add_argument("--distros", help="add Linux releases, e.g. ubuntu:22.04,debian:12,rhel:8,alma:9")
    sync.add_argument("--windows", help="add Windows Server versions, e.g. 2016,2019,2022,2025")
    sync.add_argument("--cisco", help="add Cisco versions, e.g. 'IOS XE|17.9.4a,ASA|9.16(4),IOS|15.2(7)E10'")
    sync.add_argument("--nvd-products", help="add NVD products, e.g. 'talariax:sendquick,trendmicro:tippingpoint_operating_system'")
    sync.add_argument("--all", action="store_true",
                      help="download every supported Linux release and Windows Server version, not just the requested ones")
    sync.add_argument("--show-request", action="store_true", help="print what the feed folder will download, then stop")
    sync.add_argument("--skip", default="", help="feeds to skip: osv,nvd,msrc,kev,epss,cisco")
    sync.add_argument("--msrc-since", type=int, default=2022, help="first year of Microsoft updates to download")
    return p.parse_args(argv)


def run_sync(args):
    from vulnscan.feedsync import sync_all

    from vulnscan.feedsync import coverage, load_request

    out = args.out or "feeds"
    split = lambda value: [v.strip() for v in (value or "").split(",") if v.strip()]
    extra = {"distros": split(args.distros), "windows_products": split(args.windows), "cisco_versions": split(args.cisco),
             "nvd_products": split(args.nvd_products)}
    try:
        os.makedirs(out, exist_ok=True)
        req = load_request(out, args.request, extra)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        sys.exit(f"Request problem: {exc}")
    print(f"Feed folder {out} will cover:")
    distros, windows = coverage(req, args.all)
    note = " (all)" if args.all else "" if req["distros"] else " (defaults: nothing requested yet)"
    print(f"  Linux{note}: " + ", ".join(distros))
    note = " (all)" if args.all else "" if req["windows_products"] else " (defaults: nothing requested yet)"
    print(f"  Windows{note}: " + ", ".join(windows))
    print("  Cisco:   " + (", ".join(req["cisco_versions"]) or "none yet (add with --cisco or a scan's feed-request.json)"))
    print("  NVD:     all products in data/nvd_products.json (Fortinet, Juniper, Aruba, Comware, PHP, ...)"
          + (" plus " + ", ".join(req["nvd_products"]) if req["nvd_products"] else ""))
    if args.show_request:
        return 0
    print(f"Updating vulnerability feeds in {out} ...")
    manifest = sync_all(
        out,
        skip={s.strip() for s in args.skip.split(",") if s.strip()},
        nvd_api_key=os.environ.get("NVD_API_KEY"),
        msrc_since=args.msrc_since,
        cisco_id=os.environ.get("CISCO_CLIENT_ID"),
        cisco_secret=os.environ.get("CISCO_CLIENT_SECRET"),
        everything=args.all,
    )
    failed = [n for n, e in manifest["feeds"].items() if e.get("status") != "ok"]
    print(f"Done. Copy the whole '{out}' folder to the scanner." + (f" Failed this time: {', '.join(failed)}" if failed else ""))
    return 1 if failed and len(failed) == len(manifest["feeds"]) else 0


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(message)s")
    if args.sync_feeds:
        return run_sync(args)
    if not args.inventory:
        sys.exit("--inventory is required (or use --sync-feeds on the sync machine).")

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

    feeds, cisco_api = None, None
    if args.feeds:
        try:
            feeds = FeedStore(args.feeds)
        except FeedError as exc:
            sys.exit(f"Feed folder problem: {exc}")
        for warning in feeds.warnings:
            print(f"WARNING {warning}")
        kev = KEVCatalog(feeds.kev, "CISA KEV (feed folder)")
    else:
        kev = KEVCatalog.load(offline=args.no_network, snapshot_path=os.path.join(DATA_DIR, "kev_snapshot.json"))
        cid, secret = os.environ.get("CISCO_CLIENT_ID"), os.environ.get("CISCO_CLIENT_SECRET")
        if cid and secret and not args.no_network:
            cisco_api = CiscoOpenVuln(cid, secret)

    scanner = Scanner(collector, kev, cisco_api=cisco_api, allowlist=allowlist, workers=args.workers, feeds=feeds,
                      include_unfixed=args.include_unfixed)
    print(f"Scanning {len(devices)} devices ({'saved output' if args.offline else 'live'}, {args.workers} at a time)...")
    result = scanner.scan(devices)

    out = args.out or default_report_dir()
    paths = write_all(result, out, title=args.title, org=args.org)
    request_path = os.path.join(out, "feed-request.json")
    with open(request_path, "w", encoding="utf-8") as f:
        json.dump(feed_request(result.results), f, indent=2)

    counts = result.severity_counts()
    print(f"Scanned {len(result.scanned)}/{len(result.results)} devices · risk {result.risk_score()}/100 · "
          f"critical {counts['critical']} · high {counts['high']} · medium {counts['medium']} · "
          f"actively exploited {result.kev_count()}")
    for r in result.not_scanned:
        print(f"  not scanned: {r.device.label} ({r.status}: {r.error})")
    print(f"Report: {paths['html']}\nData:   {paths['json']}, {paths['csv']}")
    print(f"Feed request for the sync machine: {request_path} (OS releases and software versions only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
