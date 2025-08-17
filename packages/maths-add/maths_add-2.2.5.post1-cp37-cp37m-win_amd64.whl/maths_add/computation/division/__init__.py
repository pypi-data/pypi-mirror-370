# encoding:utf-8
from maths_add.except_error import decorate

__all__ = [
    "divisionTion"
]


@decorate()
def divisionTion(*args):
    quotient = args[0]
    args = list(args)
    args.remove(quotient)
    try:
        for i in args:
            quotient /= i
    except ZeroDivisionError:
        print("ZeroDivisionError:division by zero")
        return None
    except TypeError:
        print("TypeError:unsupported operand type(s) for /: 'int' and 'str'")
        return None
    return quotient
