import pytest
from app import calc


def test_subnet_cidr():
    d = calc.subnet_info("172.16.2.12/24")
    assert d["network"] == "172.16.2.0" and d["broadcast"] == "172.16.2.255"
    assert d["usable_hosts"] == 254 and d["class"] == "B" and d["type"] == "private"
    assert d["ip_binary"] == "10101100.00010000.00000010.00001100"


def test_subnet_mask_form():
    d = calc.subnet_info("172.16.0.0 255.128.0.0")
    assert d["prefix"] == 9 and d["netmask"] == "255.128.0.0"


def test_small_prefixes():
    assert calc.subnet_info("10.0.0.0/31")["usable_hosts"] == 2
    assert calc.subnet_info("10.0.0.5/32")["usable_hosts"] == 1


def test_ipv6():
    d = calc.subnet_info("2001:db8::1/64")
    assert d["version"] == 6 and d["network"] == "2001:db8::"


def test_types():
    assert calc.subnet_info("127.0.0.1/8")["type"] == "loopback"
    assert calc.subnet_info("8.8.8.8/32")["type"] == "public"
    assert calc.subnet_info("224.0.0.1/4")["class"] == "D (multicast)"


def test_convert():
    assert calc.convert("192.168.1.1")["hex"] == "0xC0A80101"
    assert calc.convert("0xC0A80101")["dotted"] == "192.168.1.1"
    assert calc.convert("3232235777")["dotted"] == "192.168.1.1"
    assert calc.convert("11000000.10101000.00000001.00000001")["dotted"] == "192.168.1.1"
    assert calc.convert("::1")["version"] == 6


def test_split():
    r = calc.split("192.168.0.0/24", count=4)
    assert [s["cidr"] for s in r["subnets"]] == [
        "192.168.0.0/26", "192.168.0.64/26", "192.168.0.128/26", "192.168.0.192/26"]
    assert calc.split("10.0.0.0/24", new_prefix=25)["count"] == 2
    with pytest.raises(ValueError):
        calc.split("10.0.0.0/24", new_prefix=24)


def test_vlsm():
    r = calc.vlsm("192.168.1.0/24", [{"name": "C", "hosts": 10},
                                      {"name": "A", "hosts": 100}, {"name": "B", "hosts": 50}])
    assert [(a["name"], a["cidr"]) for a in r["allocations"]] == [
        ("A", "192.168.1.0/25"), ("B", "192.168.1.128/26"), ("C", "192.168.1.192/28")]
    with pytest.raises(ValueError):
        calc.vlsm("192.168.1.0/24", [{"name": "X", "hosts": 200}, {"name": "Y", "hosts": 100}])


def test_supernet():
    r = calc.supernet(["192.168.0.0/24", "192.168.1.0/24"])
    assert r["summary"]["cidr"] == "192.168.0.0/23" and r["exact"]
    r = calc.supernet(["192.168.0.0/24", "192.168.3.0/24"])
    assert r["summary"]["cidr"] == "192.168.0.0/22" and not r["exact"]
    assert r["wasted_addresses"] == "512"


@pytest.mark.parametrize("bad", ["", "300.1.1.1/24", "10.0.0.0/33", "abc"])
def test_invalid(bad):
    with pytest.raises(ValueError):
        calc.subnet_info(bad)
