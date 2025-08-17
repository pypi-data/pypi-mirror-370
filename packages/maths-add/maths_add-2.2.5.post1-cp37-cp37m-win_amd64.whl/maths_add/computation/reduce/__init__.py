# encoding:utf-8
from maths_add.except_error import decorate

__all__ = [
    "reduceTion"
]


@decorate()
def reduceTion(*args):
    difference = args[0]
    args = list(args)
    args.remove(difference)
    for i in args:
        difference -= i
    return difference
