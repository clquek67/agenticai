"""Version comparison that copes with vendor formats.

Examples it handles: Cisco IOS ``15.2(7)E8``, IOS XE ``17.06.04`` / ``17.6.6a``,
ASA ``9.8(4)20`` and HPE Comware releases such as ``3507P10``.
Numbers compare numerically, letters alphabetically, and a version that is a
prefix of another is the older one (``17.6.6`` < ``17.6.6a``).
"""

import re

_TOKEN = re.compile(r"\d+|[A-Za-z]+")


def version_key(version):
    key = []
    for tok in _TOKEN.findall(version or ""):
        if tok.isdigit():
            key.append((0, int(tok), ""))
        else:
            key.append((1, 0, tok.lower()))
    return key


def compare(a, b):
    """Return -1, 0 or 1 as ``a`` is older than, equal to or newer than ``b``."""
    ka, kb = version_key(a), version_key(b)
    return (ka > kb) - (ka < kb)


def train(version, depth=2):
    """The release train: the first ``depth`` numbers (``17.06.04`` -> ``17.6``)."""
    nums = re.findall(r"\d+", version or "")
    return ".".join(str(int(n)) for n in nums[:depth])


def normalize_dotted(version):
    """Drop leading zeros from each dotted part (``17.06.04`` -> ``17.6.4``)."""
    return re.sub(r"(?<![\w])0+(\d)", r"\1", version or "")
