# encoding:utf-8
from maths_add.except_error import decorate

__all__ = [
    "is_self_powerful_num",
    "count_self_powerful_num",
    "print_self_powerful_num"
]


@decorate()
def is_self_powerful_num(n):
    n1 = n
    result = 0
    length = len(str(n))
    while n > 0:
        temp = n % 10
        result += temp ** length
        n //= 10
    if result == n1:
        return True
    else:
        return False


@decorate()
def count_self_powerful_num(num):
    result = 0
    for i in range(0, num + 1):
        if is_self_powerful_num(i):
            result += 1
    return result


@decorate()
def print_self_powerful_num(num):
    result = []
    for i in range(0, num + 1):
        if is_self_powerful_num(i):
            result.append(i)
    return result
