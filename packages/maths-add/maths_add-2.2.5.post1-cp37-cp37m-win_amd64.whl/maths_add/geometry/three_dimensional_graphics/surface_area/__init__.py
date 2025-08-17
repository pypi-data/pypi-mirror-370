# encoding:utf-8
import math

__all__ = [
    "_round",
    "cuboid",
    "cube",
    "cylinder",
    "cone",
    "sphere"
]

pi = math.pi


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
    if type(a) == int and type(b) == int and type(h) == int:
        return 2 * (a * b + a * h + b * h)
    length = _round(a) + _round(b) + _round(h)
    return round(2 * (a * b + a * h + b * h), length)


def cube(a):
    ERROR(a)
    if type(a) == int:
        return 6 * a * a
    length = _round(a) * 2
    return round(6 * a * a, length)


def cylinder(r, h, _pi=True):
    global pi
    ERROR(r, h)
    if _pi == False:
        return 2 * pi * r * r + 2 * pi * r * h
    if type(r) == int and type(h) == int:
        return round(2 * pi * r * r + 2 * pi * r * h, 2)
    pi = round(pi, 2)
    length = _round(r) * 2 + _round(h) + 2
    return round(2 * pi * r * r + 2 * pi * r * h, length)


def cone(r, l, _pi=True):
    global pi
    ERROR(r, l)
    if _pi == False:
        return pi * r * r + pi * r * l
    pi = round(pi, 2)
    if type(r) == int and type(l) == int:
        return round(pi * r * r + pi * r * l, 2)
    length = _round(r) * 2 + _round(l) + 2
    return round(pi * r * r + pi * r * l, length)


def sphere(r, _pi=True):
    global pi
    ERROR(r)
    if _pi == False:
        return 4 * pi * r * r
    if type(r) == int:
        return 4 * round(pi, 2) * r * r
    length = _round(r) * 2 + 2
    return round(4 * round(pi, 2) * r * r, length)
