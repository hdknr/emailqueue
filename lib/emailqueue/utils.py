from django.conf import settings

import re
import hashlib
# import traceback


def to_raw_return_path(**kwargs):
    return "{prefix}_{msg}_{to}@{domain}".format(**kwargs)


def from_raw_return_path(address):
    m = re.search("_".join([
        r"^(?P<prefix>[^_]+)",
        r"(?P<msg>[^_]+)",
        r"(?P<to>[^_]+)@(?P<domain>.+)$"]), address)
    return m and m.groupdict() or None


def get_hashcode(data):
    return "{0:x}".format(
        hash(hashlib.sha256(data + settings.SECRET_KEY).digest()))


def to_return_path(**kwargs):
    raw_return_path = to_raw_return_path(**kwargs)
    code = get_hashcode(raw_return_path)
    return "R{0}_{1}".format(code, raw_return_path)


def from_return_path(return_path):
    m = re.search(r"^R(?P<code>[^_]+)_(?P<address>.+)", return_path)
    m = m and m.groupdict() or {}
    address = m.get('address', '')
    code = get_hashcode(address)
    return (code == m.get('code', '')) and from_raw_return_path(address) or {}
