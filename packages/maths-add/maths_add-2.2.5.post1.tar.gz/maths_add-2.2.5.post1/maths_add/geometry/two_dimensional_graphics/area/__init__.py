# encoding:utf-8
import math

__all__ = [
    "_round",
    "rectangle",
    "square",
    "parallelogram",
    "triangle",
    "trapezoid",
    "circle",
    "ellipse",
    "sector",
    "leaf"
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


def rectangle(a, b):
    ERROR(a, b)
    if type(a) == int and type(b) == int:
        return a * b
    length = 0
    length += (_round(a) + _round(b))
    return round(a * b, length)


def square(a):
    ERROR(a)
    if type(a) == int:
        return a * a
    length = 0
    length += (_round(a) * 2)
    return round(a * a, length)


def parallelogram(a, h):
    ERROR(a, h)
    if type(a) == int and type(h) == int:
        return a * h
    length = 0
    length += (_round(a) + _round(h))
    return round(a * h, length)


def triangle(a, h):
    ERROR(a, h)
    if type(a) == int and type(h) == int:
        return a * h / 2
    length = 0
    length += (_round(a) + _round(h))
    if len(str(a * h / 2)) - 2 == length + 1:
        return round(a * h / 2, length + 1)
    return round(a * h / 2, length)


def trapezoid(a, b, h):
    ERROR(a, b, h)
    if type(a) == int and type(b) == int and type(h) == int:
        return (a + b) * h / 2
    length = 0
    length += (_round(a) + _round(b) + _round(h))
    return round((a + b) * h / 2, length)


def circle(r, _num=False, _pi=True):
    ERROR(r)
    if _num == True:
        num = int(input())
        return round(r * r * pi, num)
    if _pi == False:
        return r * r * pi
    if type(r) == int:
        return round(r * r * round(pi, 2), 2)
    return round(r * r * round(pi, 2), _round(r) * 2 + 2)


def ellipse(a, b, _num=False, _pi=True):
    ERROR(a, b)
    if _num == True:
        num = int(input())
        return round(a * b * pi, num)
    if _pi == False:
        return a * b * pi
    if type(a) == int and type(b) == int:
        return round(a * b * round(pi, 2), 2)
    return round(a * b * round(pi, 2), _round(a) + _round(b) * 2 + 2)


def sector(r, angle, _num=False, _pi=True):
    ERROR(r, angle)
    if _num == True:
        num = int(input())
        return round(circle(r) * (angle / 360), num)
    if _pi == False:
        return circle(r, _pi=False) * (angle / 360)
    if type(r) == int:
        return round(r * r * round(pi, 2) * (angle / 360), 2)
    return round(r * r * round(pi, 2) * (angle / 360), _round(r) * 2 + 2)


# 两条1/4圆除半径外围成的叶子
def leaf(r, _num=False, _pi=True):
    ERROR(r)
    if _num == True:
        num = int(input())
        return round(sector(r, 180) - r * r, num)
    if _pi == False:
        return sector(r, 180, _pi=False) - r * r
    if type(r) == int:
        return round(sector(r, 180) - r * r, 2)
    return round(sector(r, 180) - r * r, _round(r) * 2 + 2)
