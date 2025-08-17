# encoding:utf-8
import math
from maths_add.except_error import decorate
from maths_add.factors_and_multiples_numbers import find_factors

__all__ = [
    "isPrime",
    "countPrime",
    "printPrime",
    "prime_sieve",
    "find_prime_factors"
]

@decorate()
def isPrime(num):
    if num == 1 or num == 0:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(num)) + 1, 2):
        if num % i == 0:
            return False
    return True


@decorate()
def countPrime(n):
    count = 0
    for i in range(1, n + 1):
        if not isPrime(i):
            continue
        else:
            count += 1
    return count


@decorate()
def printPrime(n):
    result = []
    for i in range(1, n + 1):
        if not isPrime(i):
            continue
        else:
            result.append(i)
    return result


@decorate()
def prime_sieve(l: list) -> list:
    result = []
    for i in l:
        if isPrime(i):
            result.append(i)
    return result


@decorate()
def find_prime_factors(n: int) -> list:
    if isPrime(n):
        return [n]
    factors = find_factors(n)
    prime_factors = prime_sieve(factors)
    return prime_factors
