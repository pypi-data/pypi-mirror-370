# encoding:utf-8
from maths_add.except_error import decorate

__all__ = [
    "M_powersTion"
]


@decorate()
def M_powersTion(*args):
    M_powers = args[0]
    if M_powers == 1:
        return 1
    args = list(args)
    args.remove(M_powers)
    for i in args:
        temp = 1
        while temp < i:
            M_powers = M_powers ** M_powers
            temp += 1
    return M_powers
