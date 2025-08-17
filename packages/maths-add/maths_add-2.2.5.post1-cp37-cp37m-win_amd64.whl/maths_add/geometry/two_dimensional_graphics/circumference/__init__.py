# encoding:utf-8
import math

__all__ = [
    "_round",
    "circle",
    "ellipse",
    "sector"
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


def circle(d=None, r=None, _pi=True):
    try:
        ERROR(d, r)
    except TypeError:
        raise TypeError("The d and r must not be None!")
    if d is not None and r is not None:
        if d != 2 * r:
            raise ValueError("2r ≠ d")
    if d is not None and r is None:
        r = d / 2
    if r is not None:
        return round(round(2 * round(pi, 2) * r if _pi else 2 * r, 2), (_round(r) if _round(r) > 2 else 2))
    raise ValueError("Either d (diameter) or r (radius) must be provided.")


def ellipse(a, b, _pi=True):
    ERROR(a, b)
    if not _pi:
        return pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))
    return round(round(pi, 2) * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b))), (
        _round(a) if _round(a) > (_round(b) if _round(b) > 2 else 2) else (_round(b) if _round(b) > 2 else 2)))


def sector(r, angle, _pi=True):
    ERROR(r, angle)
    if not _pi:
        return circle(r=r) * (angle / 360) + 2 * r
    return round(circle(r=r) * (angle / 360) + 2 * r, 2)
