# encoding:utf-8
from maths_add.except_error import decorate

__all__ = [
    "rootTion"
]


@decorate()
def rootTion(*args):
    root = args[0]
    if root == 1:
        return 1
    args = list(args)
    args.remove(root)
    for i in args:
        root = root ** (1 / i)
    return root
