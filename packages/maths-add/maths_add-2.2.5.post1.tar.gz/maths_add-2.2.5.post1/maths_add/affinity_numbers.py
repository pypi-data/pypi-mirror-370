# encoding:utf-8
from maths_add import perfect_numbers
from maths_add.except_error import decorate

__all__ = [
    "find_factors",
    "isA_numbers",
    "countA_numbers",
    "printA_numbers"
]

find_factors = perfect_numbers.find_factors


@decorate()
def isA_numbers(n, m):
    resultN = find_factors(n)
    resultM = find_factors(m)
    resultN.remove(n)
    resultM.remove(m)
    if sum(resultN) == m and sum(resultM) == n:
        return True
    return False


@decorate()
def countA_numbers(n, m):
    result = 0
    for i in range(n, m + 1):
        for j in range(n, m + 1):
            if (isA_numbers(i, j)):
                result += 1
    return result // 2


@decorate()
def printA_numbers(n, m):
    result = []
    result1 = countA_numbers(n, m)
    for i in range(n, m + 1):
        for j in range(n, m + 1):
            if (isA_numbers(i, j)):
                result.append(i)
                result.append(j)
    return result[:result1 * 2]
