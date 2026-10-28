"""Exact version comparison for Linux packages: Debian/Ubuntu (dpkg) and RPM (RHEL, Rocky, Alma).

Both follow the package managers' own algorithms, so '8.3.6-0ubuntu0.24.04.12' sorts before
'8.3.6-0ubuntu0.24.04.13' and '1.0~rc1' sorts before '1.0', exactly as apt and dnf decide.
"""

import re


def _cmp(a, b):
    return (a > b) - (a < b)


# --- dpkg ------------------------------------------------------------------------

def _dpkg_order(c):
    if c == "~":
        return -1
    if c.isdigit():
        return 0
    if c.isalpha():
        return ord(c)
    return ord(c) + 256


def _dpkg_part(a, b):
    i = j = 0
    while i < len(a) or j < len(b):
        first_diff = 0
        while (i < len(a) and not a[i].isdigit()) or (j < len(b) and not b[j].isdigit()):
            ac = _dpkg_order(a[i]) if i < len(a) else 0
            bc = _dpkg_order(b[j]) if j < len(b) else 0
            if ac != bc:
                return _cmp(ac, bc)
            i += 1
            j += 1
        while i < len(a) and a[i] == "0":
            i += 1
        while j < len(b) and b[j] == "0":
            j += 1
        while i < len(a) and a[i].isdigit() and j < len(b) and b[j].isdigit():
            if not first_diff:
                first_diff = _cmp(a[i], b[j])
            i += 1
            j += 1
        if i < len(a) and a[i].isdigit():
            return 1
        if j < len(b) and b[j].isdigit():
            return -1
        if first_diff:
            return first_diff
    return 0


def _split_deb(v):
    epoch, _, rest = v.partition(":") if ":" in v else ("0", "", v)
    upstream, _, revision = rest.rpartition("-") if "-" in rest else (rest, "", "")
    return int(epoch or 0), upstream, revision


def dpkg_compare(a, b):
    ea, ua, ra = _split_deb(a)
    eb, ub, rb = _split_deb(b)
    return _cmp(ea, eb) or _dpkg_part(ua, ub) or _dpkg_part(ra, rb)


# --- rpm -------------------------------------------------------------------------

_RPM_SEG = re.compile(r"(\d+|[a-zA-Z]+|~|\^)")


def _rpmvercmp(a, b):
    if a == b:
        return 0
    sa, sb = _RPM_SEG.findall(a), _RPM_SEG.findall(b)
    while sa or sb:
        x = sa.pop(0) if sa else None
        y = sb.pop(0) if sb else None
        if x == "~" or y == "~":
            if x != y:
                return -1 if x == "~" else 1
            continue
        if x == "^" or y == "^":
            if x is None:
                return -1
            if y is None:
                return 1
            if x != y:
                return 1 if x == "^" else -1
            continue
        if x is None:
            return -1
        if y is None:
            return 1
        if x.isdigit() and y.isdigit():
            r = _cmp(int(x), int(y))
        elif x.isdigit() or y.isdigit():
            return 1 if x.isdigit() else -1  # numeric segments are newer than alpha
        else:
            r = _cmp(x, y)
        if r:
            return r
    return 0


def _split_rpm(v):
    epoch, _, rest = v.partition(":") if ":" in v else ("0", "", v)
    version, _, release = rest.rpartition("-") if "-" in rest else (rest, "", "")
    return int(epoch or 0), version, release


def rpm_compare(a, b):
    ea, va, ra = _split_rpm(a)
    eb, vb, rb = _split_rpm(b)
    return _cmp(ea, eb) or _rpmvercmp(va, vb) or _rpmvercmp(ra, rb)


def dotted_compare(a, b):
    """Windows builds such as 10.0.20348.2700."""
    pa = [int(x) for x in re.findall(r"\d+", a)]
    pb = [int(x) for x in re.findall(r"\d+", b)]
    return _cmp(pa, pb)
