# encoding:utf-8
import math
from maths_add.except_error import decorate

result = 0

__all__ = [
    "find_factors",
    "isPerfectNum",
    "countPerfectNum",
    "printPerfectNum"
]


@decorate()
def find_factors(n):
    factors = [1]
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n / i:
                factors.append(n / i)
    factors.append(n)
    return factors


@decorate()
def isPerfectNum(n) -> bool:
    factors = find_factors(n)
    factors.remove(n)
    factorsSum = 0
    for i in factors:
        factorsSum += i
    if factorsSum == n:
        return True
    return False


@decorate()
def perfect_num(n, L_func):
    global result
    for i in range(2, n + 1):
        if isPerfectNum(i):
            L_func()


@decorate()
def countPerfectNum(n) -> int:
    global result

    def in_func():
        global result
        result += 1

    perfect_num(n, in_func)
    return result


@decorate()
def printPerfectNum(n):
    result1 = []
    for i in range(2, n + 1):
        if isPerfectNum(i):
            result1.append(i)
    return result1
