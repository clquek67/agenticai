import os

from vulnscan.collectors import OfflineCollector
from vulnscan.models import Device
from vulnscan.platforms import get_platform

OFFLINE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "offline")


def parse(host, platform):
    p = get_platform(platform)
    return p.parse(OfflineCollector(OFFLINE).collect(Device(host=host, platform=platform), p))


def test_ios_classic():
    f = parse("10.10.0.11", "cisco_ios")
    assert (f.model, f.os_name, f.version, f.hostname) == ("WS-C2960X-24TS-L", "IOS", "15.2(7)E8", "sw-access-01")
    assert f.serial == "FOC0000X0AB"


def test_ios_old_router():
    f = parse("10.10.0.2", "cisco_ios")
    assert (f.model, f.version) == ("2811", "15.1(4)M12a")


def test_ios_xe():
    f = parse("10.10.0.1", "cisco_ios")
    assert (f.model, f.os_name, f.version) == ("ISR4331/K9", "IOS XE", "17.06.04")


def test_asa():
    f = parse("10.30.5.20", "cisco_asa")
    assert (f.model, f.version, f.hostname, f.serial) == ("ASA5525", "9.8(4)15", "asa-dmz-01", "FCH0000A0BC")


def test_comware7():
    f = parse("10.20.0.5", "hpe_comware")
    assert f.model == "5130-48G-PoE+-4SFP+ (370W) EI"
    assert (f.os_name, f.version, f.release, f.hostname) == ("Comware 7", "7.1.070", "3208P10", "sw-core-01")


def test_comware5():
    f = parse("10.20.0.6", "hpe_comware")
    assert f.model == "A5500-24G-4SFP HI"
    assert (f.os_name, f.release) == ("Comware 5", "5501P28")
