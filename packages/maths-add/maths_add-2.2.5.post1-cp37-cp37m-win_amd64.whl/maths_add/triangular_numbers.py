# encoding:utf-8
from maths_add.except_error import decorate
from maths_add.perfect_numbers import find_factors as factors

__all__ = [
    "isTriangular_number",
    "countTriangular_number",
    "printTriangular_number"
]

@decorate()
def isTriangular_number(n):
    factorsList = factors(n * 2)
    if factorsList[len(factorsList) // 2] + 1 == factorsList[len(factorsList) // 2 + 1]:
        return True
    else:
        return False


@decorate()
def countTriangular_number(n):
    count = 0
    for i in range(1, n + 1):
        if isTriangular_number(i) == False:
            continue
        else:
            count += 1
    return count


@decorate()
def printTriangular_number(n):
    result = []
    for i in range(1, n + 1):
        if isTriangular_number(i) == False:
            continue
        else:
            result.append(i)
    return result
