# encoding:utf-8
import math
from maths_add.except_error import decorate
import maths_add.example as e

__all__ = [
    "Pi",
    "E",
    "Tau",
    "Inf",
    "Nan",
    "获取小数点后的位数",
    "isTwoNum",
    "fastPower",
    "bubble_sort",
    "insertion_sort",
    "selection_sort",
    "merge_sort"
]


class Pi(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.pi


class E(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.e


class Tau(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.tau


class Inf(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.inf


class Nan(object):
    def __init__(self):
        pass

    def get_num(self):
        return math.nan


@decorate()
def 获取小数点后的位数(f):
    if type(f) != float:
        raise TypeError("The f must be a float.")
    f = str(f)
    fl = f.split(".")
    return len(fl[1])


_isTwoNum = lambda x: x % 2 == 0


@decorate()
def isTwoNum(x):
    return _isTwoNum(x)


@decorate()
def fastPower(a, b, k):
    r = e.fastPower(a, b, k)
    return r


@decorate()
def bubble_sort(l):
    l = e.bubble_sort(l)
    return l


@decorate()
def insertion_sort(l):
    l = e.insertion_sort(l)
    return l


@decorate()
def selection_sort(l):
    l = e.selection_sort(l)
    return l


@decorate()
def merge_sort(l):
    l = e.merge_sort(l)
    return l
