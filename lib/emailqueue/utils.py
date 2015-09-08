from django import VERSION
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
    '''Parse parameter fomm actual email address.

    :param str address: email address
    :return dict:

    Address Format::

        {{ handler_name }}_{{arg0}}_{{arg1}....@{{ domain }}

    '''
    m = re.search(
        r"^(?P<handler>[^_]+)_(?P<args>[^@]+)@(?P<domain>.+)$",
        address)
    m = m and m.groupdict() or {
        'handler': DEFAULT_HANDLER,
        'domain': address.split('@')[1]}
    m['args'] = tuple(m.get('args', '').split('_'))
    return m


def get_hashcode(data):
    return "{0:x}".format(
        hash(hashlib.sha256(data + settings.SECRET_KEY).digest()))


def to_return_path(handler, domain, *args):
    raw_return_path = to_raw_return_path(handler, domain, *args)
    code = get_hashcode(raw_return_path)
    return "R{0}_{1}".format(code, raw_return_path)


def from_return_path(return_path):
    '''Parse parameter from :term:`Return_Path` address

    Return_Path :  R{{ hash_code}}_{{ actual_address }}

    :param str return_path: Return_Path address
    :return dict: { 'hander': 'handler_name', 'args': [arg0, arg1,..], }

    - if hash code is verified, deligate  to `from_raw_return_path` function

    '''
    m = re.search(r"^R(?P<code>[^_]+)_(?P<address>.+)", return_path)
    m = m and m.groupdict() or {}
    address = m.get('address', '')
    code = get_hashcode(address)
    if code == m.get('code', ''):
        return from_raw_return_path(address)
    return {'handler': DEFAULT_HANDLER,
            'domain': return_path.split('@')[1], 'args': ()}


if VERSION < (1, 8):
    def get_template_loaders():
        from django.template import loader
        return tuple(
            loader.find_template_loader(i)
            for i in settings.TEMPLATE_LOADERS
        )
else:
    def get_template_loaders():
        from django.template import engine
        return engine.Engine.get_default().template_loaders


def get_template_source(name):
    '''
    :rtype: tuple(source text, path)
    '''
    for loader in get_template_loaders():
        try:
            return loader.load_template_source(name)
        except:
            pass
    return (None, None)
