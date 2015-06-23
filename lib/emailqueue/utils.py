from django.conf import settings

import re
import hashlib
# import traceback

DEFAULT_HANDLER = 'direct'


def to_raw_return_path(handler, domain, *args):
    return "{handler}_{args}@{domain}".format(
        handler=handler, domain=domain,
        args="_".join(map(lambda i: str(i), args)))


def from_raw_return_path(address):
    m = re.search(
        r"^(?P<handler>[^_]+)_(?P<args>[^@]+)@(?P<domain>.+)$",
        address)
    m = m and m.groupdict() or {
        'handler': DEFAULT_HANDLER,
        'domain': address.split('@')[1]}
    m['args'] = m.get('args', '').split('_')
    return m


def get_hashcode(data):
    return "{0:x}".format(
        hash(hashlib.sha256(data + settings.SECRET_KEY).digest()))


def to_return_path(handler, domain, *args):
    raw_return_path = to_raw_return_path(handler, domain, *args)
    code = get_hashcode(raw_return_path)
    return "R{0}_{1}".format(code, raw_return_path)


def from_return_path(return_path):
    m = re.search(r"^R(?P<code>[^_]+)_(?P<address>.+)", return_path)
    m = m and m.groupdict() or {}
    address = m.get('address', '')
    code = get_hashcode(address)
    if code == m.get('code', ''):
        return from_raw_return_path(address)
    return {'handler': DEFAULT_HANDLER, 'domain': '', 'args': ()}
