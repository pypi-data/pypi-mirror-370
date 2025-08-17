# encoding:utf-8
from maths_add.except_error import decorate

__all__ = [
    "isPalindromic_number",
    "countPalindromic_number",
    "printPalindromic_number"
]


@decorate()
def isPalindromic_number(n):
    oldN = n
    Rn = 0
    while n > 0:
        Rn = Rn * 10 + n % 10
        n //= 10
    if Rn == oldN:
        return True
    else:
        return False


@decorate()
def countPalindromic_number(n):
    count = 0
    for i in range(1, n + 1):
        if not isPalindromic_number(i):
            continue
        else:
            count += 1
    return count


@decorate()
def printPalindromic_number(n):
    result = []
    for i in range(1, n + 1):
        if not isPalindromic_number(i):
            continue
        else:
            result.append(i)
    return result
