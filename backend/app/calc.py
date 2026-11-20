"""Pure calculation logic built on Python's ipaddress module."""
import ipaddress as ip

MAX_SUBNETS = 4096


def parse_interface(text: str):
    """'172.16.2.12/24' or '172.16.0.0 255.128.0.0' -> IPv4/IPv6Interface."""
    t = " ".join(text.split())
    if not t:
        raise ValueError("Input is empty")
    if " " in t:
        addr, mask = t.split(" ", 1)
        t = f"{addr}/{mask.strip()}"
    return ip.ip_interface(t)


def _bin(a) -> str:
    return ".".join(f"{o:08b}" for o in a.packed)


def ip_class(a) -> str:
    if a.version != 4:
        return "n/a (IPv6)"
    first = a.packed[0]
    for limit, name in ((128, "A"), (192, "B"), (224, "C"), (240, "D (multicast)")):
        if first < limit:
            return name
    return "E (reserved)"


def ip_type(a) -> str:
    if a.version == 4 and a == ip.IPv4Address("255.255.255.255"):
        return "broadcast"
    for name, flag in (
        ("loopback", a.is_loopback),
        ("link-local", a.is_link_local),
        ("multicast", a.is_multicast),
        ("unspecified", a.is_unspecified),
        ("private", a.is_private),
        ("reserved", a.is_reserved),
    ):
        if flag:
            return name
    return "public"


def net_fields(n) -> dict:
    p = n.prefixlen
    if n.version == 6:
        return {
            "network": str(n.network_address), "prefix": p, "cidr": str(n),
            "first_address": str(n.network_address),
            "last_address": str(n.broadcast_address),
            "total_addresses": str(n.num_addresses),
        }
    if p == 32:
        first = last = n.network_address
        usable = 1
    elif p == 31:  # point-to-point (RFC 3021)
        first, last, usable = n.network_address, n.broadcast_address, 2
    else:
        first, last = n.network_address + 1, n.broadcast_address - 1
        usable = n.num_addresses - 2
    return {
        "network": str(n.network_address), "prefix": p, "cidr": str(n),
        "netmask": str(n.netmask), "wildcard": str(n.hostmask),
        "broadcast": str(n.broadcast_address),
        "first_host": str(first), "last_host": str(last),
        "total_addresses": n.num_addresses, "usable_hosts": usable,
    }


def subnet_info(text: str) -> dict:
    iface = parse_interface(text)
    a, n = iface.ip, iface.network
    d = {"address": str(a), "version": a.version, **net_fields(n),
         "class": ip_class(a), "type": ip_type(a)}
    if a.version == 4:
        d.update(ip_binary=_bin(a), netmask_binary=_bin(n.netmask),
                 ip_hex=f"0x{int(a):08X}", ip_decimal=int(a))
    else:
        d.update(address_exploded=a.exploded, ip_hex=f"0x{int(a):032X}")
    return d


def convert(value: str) -> dict:
    """Dotted / binary / hex / decimal / IPv6 -> every representation."""
    v = value.strip()
    if not v:
        raise ValueError("Input is empty")
    parts = v.split(".")
    if ":" in v:
        a = ip.IPv6Address(v)
    elif len(parts) == 4 and all(len(p) == 8 and set(p) <= {"0", "1"} for p in parts):
        a = ip.IPv4Address(".".join(str(int(p, 2)) for p in parts))
    elif "." in v:
        a = ip.IPv4Address(v)
    elif v.lower().startswith("0x"):
        n = int(v, 16)
        a = ip.IPv4Address(n) if n <= 0xFFFFFFFF else ip.IPv6Address(n)
    elif set(v) <= {"0", "1"} and len(v) == 32:
        a = ip.IPv4Address(int(v, 2))
    elif v.isdigit():
        a = ip.IPv4Address(int(v))
    else:
        raise ValueError("Unrecognised format (use dotted, binary, 0x hex or decimal)")
    if a.version == 4:
        return {"version": 4, "dotted": str(a), "binary": _bin(a),
                "hex": f"0x{int(a):08X}", "decimal": int(a),
                "class": ip_class(a), "type": ip_type(a)}
    return {"version": 6, "compressed": a.compressed, "exploded": a.exploded,
            "hex": f"0x{int(a):032X}", "decimal": str(int(a)), "type": ip_type(a)}


def split(text: str, new_prefix: int | None = None, count: int | None = None) -> dict:
    n = parse_interface(text).network
    if count is not None:
        if count < 2:
            raise ValueError("count must be at least 2")
        new_prefix = n.prefixlen + (count - 1).bit_length()
    if new_prefix is None:
        raise ValueError("Provide new_prefix or count")
    if not n.prefixlen < new_prefix <= n.max_prefixlen:
        raise ValueError(f"new prefix must be between /{n.prefixlen + 1} and /{n.max_prefixlen}")
    if 2 ** (new_prefix - n.prefixlen) > MAX_SUBNETS and count is None:
        raise ValueError(f"Too many subnets (max {MAX_SUBNETS})")
    subs = []
    for s in n.subnets(new_prefix=new_prefix):
        subs.append(net_fields(s))
        if len(subs) >= (count or MAX_SUBNETS):
            break
    return {"parent": str(n), "new_prefix": new_prefix, "count": len(subs), "subnets": subs}


def vlsm(text: str, reqs: list[dict]) -> dict:
    n = parse_interface(text).network
    if n.version != 4:
        raise ValueError("VLSM supports IPv4 only")
    if not reqs:
        raise ValueError("Add at least one requirement")
    cursor, end, used, out = int(n.network_address), int(n.broadcast_address) + 1, 0, []
    for r in sorted(reqs, key=lambda r: -r["hosts"]):
        if r["hosts"] < 1:
            raise ValueError(f"'{r['name']}': hosts must be at least 1")
        bits = (r["hosts"] + 1).bit_length()  # smallest 2**bits >= hosts + 2
        size = 1 << bits
        cursor = -(-cursor // size) * size  # align to block size
        if cursor + size > end:
            raise ValueError(f"Not enough space in {n} for '{r['name']}'")
        sub = ip.IPv4Network((cursor, 32 - bits))
        out.append({"name": r["name"], "requested_hosts": r["hosts"], **net_fields(sub)})
        cursor += size
        used += size
    return {"parent": str(n), "allocations": out,
            "addresses_used": used, "addresses_free": n.num_addresses - used}


def supernet(texts: list[str]) -> dict:
    nets = [parse_interface(t).network for t in texts]
    if len(nets) < 2:
        raise ValueError("Provide at least two networks")
    if len({n.version for n in nets}) != 1:
        raise ValueError("Cannot mix IPv4 and IPv6")
    bits = nets[0].max_prefixlen
    lo = min(int(n.network_address) for n in nets)
    hi = max(int(n.broadcast_address) for n in nets)
    prefix = bits - (lo ^ hi).bit_length()
    shift = bits - prefix
    summary = type(nets[0])(((lo >> shift) << shift, prefix))
    agg = list(ip.collapse_addresses(nets))
    covered = sum(n.num_addresses for n in agg)
    return {"summary": net_fields(summary), "exact": covered == summary.num_addresses,
            "aggregated": ", ".join(str(n) for n in agg),
            "wasted_addresses": str(summary.num_addresses - covered)}
