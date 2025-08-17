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
        return a * b * h
    length = _round(a) + _round(b) + _round(h)
    return round(a * b * h, length)


def cube(a):
    ERROR(a)
    if type(a) == int:
        return a * a * a
    length = _round(a) * 3
    return round(a * a * a, length)


def cylinder(r, h, _pi=True):
    global pi
    ERROR(r, h)
    if _pi == False:
        return pi * r * r * h
    pi = round(pi, 2)
    if type(r) == int and type(h) == int:
        return round(pi * r * r * h, 2)
    length = _round(r) * 2 + _round(h) + 2
    return round(pi * r * r * h, length)


def cone(r, h, _pi=True):
    global pi
    ERROR(r, h)
    return round(cylinder(r, h, _pi=_pi) / 3, 15)


def sphere(r, _pi=True):
    ERROR(r)
    if _pi == False:
        return 4 / 3 * pi * r * r * r
    if type(r) == int:
        return 4 / 3 * pi * r * r * r
    length = _round(r) * 3 + 2
    return round(4 / 3 * round(pi, 2) * r * r * r, length)
