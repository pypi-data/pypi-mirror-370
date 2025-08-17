# encoding:utf-8

__all__ = [
    "_round",
    "rectangle",
    "square",
    "parallelogram",
    "triangle",
    "trapezoid"
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


def rectangle(a, b):
    ERROR(a, b)
    if type(a) == int and type(b) == int:
        return (a + b) * 2
    length = 0
    length += (_round(a) if _round(a) > _round(b) else _round(b))
    return round((a + b) * 2, length)


def square(a):
    ERROR(a)
    if type(a) == int:
        return a * 4
    length = 0
    length += (_round(a))
    return round(a * 4, length)


def parallelogram(a, b):
    return rectangle(a, b)


def triangle(a, b, c):
    ERROR(a, b, c)
    if type(a) == int and type(b) == int and type(c) == int:
        return a + b + c
    length = 0
    length += _round(max(a, b, c))
    return round(a + b + c, length)


def trapezoid(a, b, c, d):
    ERROR(a, b, c, d)
    if type(a) == int and type(b) == int and type(c) == int and type(d) == int:
        return a + b + c + d
    length = 0
    length += _round(max(a, b, c, d))
    return round(a + b + c + d, length)
