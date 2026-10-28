# Example feed folder

Used by the offline demo (`--feeds examples/feeds`). It is **not** a real feed folder:

- `osv-ubuntu`, `osv-rocky`: real OSV.dev data, cut down to the PHP packages of the example servers.
- `kev`: real CISA KEV entries for the CVEs the demo devices hit.
- `msrc`, `nvd`: **sample entries with fake IDs** (`SAMPLE-...`) that show the format.

Create a real one on an internet-connected machine with `python scan.py --sync-feeds --out feeds`.
Because this folder is not refreshed, the scanner will warn that it is old: that is expected.
