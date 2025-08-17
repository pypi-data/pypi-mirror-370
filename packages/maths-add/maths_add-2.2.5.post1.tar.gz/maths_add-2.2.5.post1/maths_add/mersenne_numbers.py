# encoding:utf-8
from maths_add import prime_numbers
from maths_add.except_error import decorate
from maths_add.advanced_computation import logarithm

__all__ = [
    "isPrime",
    "isMersenne",
    "isMersennePrime",
    "countMersenne",
    "countMersennePrime",
    "printMersenne",
    "printMersennePrime"
]

isPrime = prime_numbers.isPrime


@decorate()
def isMersenne(Mp):
    p = logarithm.logTion(Mp + 1, 2)
    if isPrime(p):
        return True
    else:
        return False


@decorate()
def countMersenne(n):
    count = 0
    for i in range(1, n + 1):
        if isMersenne(i) == False:
            continue
        else:
            count += 1
    return count


@decorate()
def printMersenne(n):
    result = []
    for i in range(1, n + 1):
        if isMersenne(i) == False:
            continue
        else:
            result.append(i)
    return result


@decorate()
def isMersennePrime(Mp):
    if isMersenne(Mp) is False and isPrime(Mp) is False:
        return False
    else:
        return True


@decorate()
def countMersennePrime(n):
    count = 0
    for i in range(1, n + 1):
        if isMersennePrime(i) is False:
            continue
        else:
            count += 1
    return count


@decorate()
def printMersennePrime(n):
    result = []
    for i in range(1, n + 1):
        if isMersennePrime(i) is False:
            continue
        else:
            result.append(i)
    return result
