# encoding:utf-8
from maths_add.except_error import decorate

__all__ = [
    "addTion"
]


@decorate()
def addTion(*args):
    sum = 0
    for i in args:
        sum += i
    return sum
