# encoding:utf-8

__all__ = [
    "_round",
    "cuboid",
    "cube",
    "prism",
    "pyramid"
]


def _round(a):
    if type(a) == int:
        return 0
    _a = str(a)
    length = len(_a) - 2
    return length


def ERROR(*args):
    for i in args:
        if type(i) != int and type(i) != float:
            r1 = "must be a int or a float, not " + str(type(i).__name__)
            raise TypeError(r1)


def cuboid(a, b, h):
    ERROR(a, b, h)
    if type(a) == int and type(b) == int and type(h) == int: return (a + b + h) * 4
    length = 0
    length += _round(max(a, b, h))
    return round((a + b + h) * 4, length)


def cube(a):
    ERROR(a)
    if type(a) == int: return a * 12
    length = 0
    length += _round(a)
    return round(a * 12, length)


def prism(n, a, h):
    ERROR(n, a, h)
    if type(n) == float: raise TypeError("The n is not a int")
    length = 0
    if type(a) == float: length += _round(a)
    if type(h) == float: length += _round(h)
    if length == 0: return n * h + 2 * n * a
    return round(n * h + 2 * n * a, length)


def pyramid(n, a, h):
    ERROR(n, a, h)
    if type(n) == float: raise TypeError("The n is not a int")
    length = 0
    if type(a) == float: length += _round(a)
    if type(h) == float: length += _round(h)
    if length == 0: return n * (a + h)
    return round(n * (a + h), length)
