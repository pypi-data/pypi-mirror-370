# encoding:utf-8
from functools import lru_cache
from maths_add.except_error import decorate

__all__ = [
    "decorate_main",
    "general_term_extreme",
    "general_term_inefficient",
    "List_extreme",
    "List_inefficient",
    "List_2_inefficient"
]


def decorate_main(func):
    cached_func = lru_cache(maxsize=None)(func)

    def wrapper(*args, **kwargs):
        result = cached_func(*args, **kwargs)
        return result

    return wrapper


@decorate()
def general_term_extreme(n):
    result = 0
    first = 1
    second = 1
    for _ in range(0, n - 2):
        result = (first + second)
        first = second
        second = result
    return result


@decorate()
def general_term_inefficient(n):
    if n == 1 or n == 2:
        return 1
    return general_term_inefficient(n - 1) + general_term_inefficient(n - 2)


@decorate()
def List_extreme(n):
    result_list = [1, 1]
    result = 0
    first = 1
    second = 1
    for _ in range(0, n - 2):
        result = (first + second)
        first = second
        second = result
        result_list.append(result)
    return result_list


@decorate()
# 不推荐递归函数
# 在List_inefficient里不能填过大的数
def List_inefficient(n):
    result_list = [1, 1]

    def in_func(n):
        if n == 1 or n == 2:
            return 1
        return in_func(n - 1) + in_func(n - 2)

    for i in range(3, n + 1):
        result_list.append(in_func(i))
    return result_list


@decorate()
def List_2_inefficient(n):
    result_list = [1, 1]
    result_dict = {1: 1, 2: 2}

    def in_func(n):
        if n == 1 or n == 2:
            return 1
        if n in result_dict:
            return result_dict[n]
        result_dict[n] = in_func(n - 1) + in_func(n - 2)
        return result_dict[n]

    for i in range(3, n + 1):
        result_list.append(in_func(i))
    return result_list
