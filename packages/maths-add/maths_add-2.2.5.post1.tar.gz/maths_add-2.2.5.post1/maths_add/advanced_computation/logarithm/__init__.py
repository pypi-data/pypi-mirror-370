# encoding:utf-8
import math
from maths_add.except_error import decorate

__all__ = [
    "logTion"
]

@decorate()
def logTion(*args):
    log = args[0]
    args = list(args)
    args.remove(log)
    for i in args:
        log = math.log(log, i)
    return log
