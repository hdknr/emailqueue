from enum import Enum as BaseEnum


def Enum(name, **param):
    items = dict((k, v[0]) for k, v in param.items())
    newenum = type(name, (BaseEnum, ), items)
    for k in param:
        item = getattr(newenum, k)
        setattr(item, 'description', param[k][1])
    newenum.choices = tuple(v for k, v in param.items())
    return newenum
