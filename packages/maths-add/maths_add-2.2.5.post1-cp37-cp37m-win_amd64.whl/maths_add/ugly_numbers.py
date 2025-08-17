# encoding:utf-8
from maths_add.except_error import decorate

__all__ = [
    "ugly_num",
    "List_ugly_num"
]


@decorate()
def ugly_num(n):
    result = [1]
    i2, i3, i5 = 0, 0, 0
    next2, next3, next5 = 2, 3, 5
    for i in range(1, n):
        next_num = min(next2, next3, next5)
        result.append(next_num)
        if next_num == next2:
            i2 += 1
            next2 = result[i2] * 2
        if next_num == next3:
            i3 += 1
            next3 = result[i3] * 3
        if next_num == next5:
            i5 += 1
            next5 = result[i5] * 5
    return result[n - 1]


@decorate()
def List_ugly_num(n):
    result = [1]
    i2, i3, i5 = 0, 0, 0
    next2, next3, next5 = 2, 3, 5
    for i in range(1, n):
        next_num = min(next2, next3, next5)
        result.append(next_num)
        if next_num == next2:
            i2 += 1
            next2 = result[i2] * 2
        if next_num == next3:
            i3 += 1
            next3 = result[i3] * 3
        if next_num == next5:
            i5 += 1
            next5 = result[i5] * 5
    return result
