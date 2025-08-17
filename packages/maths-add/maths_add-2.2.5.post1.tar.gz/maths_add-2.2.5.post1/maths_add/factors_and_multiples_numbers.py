# encoding:utf-8
from maths_add.perfect_numbers import find_factors as factors
from maths_add.except_error import decorate
import random

__all__ = [
    "find_factors",
    "find_multiples",
    "the_Same_factors",
    "the_Same_multiples",
    "the_Biggest_Same_factors",
    "the_Smallest_Same_multiples",
    "gcd",
    "lcm"
]


@decorate()
def find_factors(*args, **kwargs):
    return factors(*args, **kwargs)


@decorate()
def find_multiples(a, n):
    result = []
    for i in range(1, n + 1):
        result.append(a * i)
    return result


@decorate()
def the_Same_factors(a, b):
    aList = find_factors(a)
    bList = find_factors(b)
    result = []
    for i in aList:
        for j in bList:
            if i == j:
                result.append(i)
    return result


@decorate()
def the_Same_multiples(a, b):
    aList = find_multiples(a, b)
    bList = find_multiples(b, a)
    result = []
    for i in aList:
        for j in bList:
            if i == j:
                result.append(i)
    return result


@decorate()
def the_Biggest_Same_factors(a, b, version=1.0):
    if the_Smallest_Same_multiples(a, b) == a * b:
        return 1
    elif version == 1.0:
        aList = find_factors(a)
        bList = find_factors(b)
        result = 1
        for i in aList:
            for j in bList:
                if i == j and i > result:
                    result = i
    elif version == 2.0:
        result = a * b / the_Smallest_Same_multiples(a, b, version=float(random.randint(1, 2)))
    return result


@decorate()
def the_Smallest_Same_multiples(a, b, version=1.0):
    if the_Biggest_Same_factors(a, b) == 1:
        return a * b
    elif version == 1.0:
        result = a * b / the_Biggest_Same_factors(a, b, version=float(random.randint(1, 2)))
    elif version == 2.0:
        aList = find_multiples(a, b)
        bList = find_multiples(b, a)
        result = a * b
        for i in aList:
            for j in bList:
                if i == j and i < result:
                    result = i
    return result


@decorate()
def gcd(a, b):
    if a % b == 0:
        return b
    return gcd(b, a % b)


@decorate()
def lcm(a, b):
    return a * b / gcd(a, b)
