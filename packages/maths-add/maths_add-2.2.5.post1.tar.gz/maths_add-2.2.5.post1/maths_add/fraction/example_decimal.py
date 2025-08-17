# encoding:utf-8
import math
from fractions import Fraction
import sympy
from sympy import sympify
from maths_add.except_error import decorate
from maths_add.prime_numbers import find_prime_factors
from maths_add.fraction.code import Hf
from decimal import Decimal, getcontext

__all__ = [
    "decimal_to_fraction",
    "empty",
    "is_terminating_decimal",
    "is_recurring_decimal",
    "isNrNt_decimal",
]

sympy.init_printing()

getcontext().prec = 100


def decimal_to_fraction(d: Decimal) -> Fraction:
    """将Decimal转换为最简分数"""
    # 处理整数部分和小数部分
    sign = -1 if d < 0 else 1
    d_abs = abs(d)
    integer_part = int(d_abs)  # 整数部分
    fractional_part = d_abs - integer_part  # 小数部分
    # 小数部分转为分数（如0.333... → 333.../10^n）
    fractional_str = format(fractional_part, f'.{getcontext().prec}f').split('.')[1].rstrip('0')
    if not fractional_str:  # 无小数部分（整数）
        return Fraction(integer_part * sign, 1)
    # 组合整数和小数部分为分数
    numerator = integer_part * (10 ** len(fractional_str)) + int(fractional_str)
    denominator = 10 ** len(fractional_str)
    fraction = Fraction(numerator, denominator) * sign
    return fraction  # 自动化简为最简分数


@decorate()
def empty(l: list) -> bool:
    try:
        l[0]
    except IndexError:
        return True
    return False


@decorate()
def is_terminating_decimal(n: Fraction, isPrintFloat=False):
    prime_factors = find_prime_factors(n.denominator)
    prime_factors = list(set(prime_factors))
    prime_factors = [p for p in prime_factors if p not in {2, 5}]  # 简化移除逻辑
    if isPrintFloat:
        return empty(prime_factors)
    else:
        return False if empty(prime_factors) else Hf().fzx(n)  # 有限小数 → 返回小数值


@decorate()
def is_recurring_decimal(f: Decimal) -> bool:
    return not is_terminating_decimal(decimal_to_fraction(f))


@decorate()
def isNrNt_decimal(expr) -> bool:
    try:
        # 将输入转换为 sympy 符号表达式（保留精确数学意义）
        sym_expr = sympify(expr)
    except (sympy.SympifyError, TypeError):
        # 无法转换为有效表达式（如非数学字符串）
        raise ValueError(f"无法解析表达式: {expr}")

        # 无理数的定义：不是有理数的实数（即无限不循环小数）
    return not sym_expr.is_rational
