# encoding:utf-8
from __future__ import annotations
from math import sqrt, floor, atan2, exp, log, cos, sin, isclose
from typing import Union
from maths_add.except_error import decorate
from fractions import Fraction
import warnings

__all__ = [
    "Complex"
]

class FloatWarnings(UserWarning):
    pass


def ERROR(args, typeList):
    for arg in args:
        is_valid = False
        for t in typeList:
            if isinstance(arg, t):
                is_valid = True
                break
        if not is_valid:
            raise TypeError(f"The arg must be one of the following types: {typeList}.")


@decorate()
class Complex(object):
    # 仅包含支持real和imag属性的类型（自身和内置complex）
    _complex_type = (complex,)

    @decorate()
    def __init__(self, real, imag, isOuter=True):
        # 实部和虚部支持int, float, Fraction
        ERROR([real, imag], [int, float, Fraction])
        # 分数类型警告
        if (isinstance(real, Fraction) or isinstance(imag, Fraction)) and isOuter:
            warnings.warn("The real and imag are recommended to be int or float.", FloatWarnings)
        self.real = real  # 实部
        self.imag = imag  # 虚部
        self.isOuter = isOuter
        if self.__class__ not in Complex._complex_type:
            Complex._complex_type = Complex._complex_type + (self.__class__,)

    def zero(self, n: Union[int, float, Fraction, complex, Complex]):
        if isinstance(n, (complex, self.__class__)):
            if n.real == 0 and n.imag == 0:
                raise ZeroDivisionError("除数不能为零")
        else:
            if n == 0:
                raise ZeroDivisionError("除数不能为零")

    @decorate()
    def __del__(self):
        if self.isOuter:
            print("对象被销毁")

    @decorate()
    def __str__(self):
        if self.imag > 0:
            return f"{self.real}+{self.imag}i"
        elif self.imag == 0:
            return f"{self.real}"
        else:
            return f"{self.real}{self.imag}i"  # 负虚部自动显示为减号

    @decorate()
    def __repr__(self):
        return f"Complex(real={self.real}, imag={self.imag})"

    @decorate()
    def __abs__(self):
        """复数的模：√(real² + imag²)"""
        return sqrt(self.real ** 2 + self.imag ** 2)

    @decorate()
    def __add__(self, other):
        """复数加法：(a+bi) + (c+di) = (a+c)+(b+d)i"""
        if not isinstance(other, Complex._complex_type):
            return NotImplemented
        return Complex(
            self.real + other.real,
            self.imag + other.imag,
            isOuter=False
        )

    @decorate()
    def __radd__(self, other):
        """反向加法：other + self（处理int/float/Fraction/complex）"""
        if isinstance(other, (int, float, Fraction)):
            oc = Complex(other, 0, isOuter=False)  # 转换为实部为other的复数
        elif isinstance(other, complex):
            oc = Complex(other.real, other.imag, isOuter=False)  # 内置complex转换
        else:
            return NotImplemented
        return oc + self

    @decorate()
    def __sub__(self, other):
        """复数减法：(a+bi) - (c+di) = (a-c)+(b-d)i"""
        if not isinstance(other, Complex._complex_type):
            return NotImplemented
        return Complex(
            self.real - other.real,
            self.imag - other.imag,
            isOuter=False
        )

    @decorate()
    def __rsub__(self, other):
        """反向减法：other - self"""
        if isinstance(other, (int, float, Fraction)):
            oc = Complex(other, 0, isOuter=False)
        elif isinstance(other, complex):
            oc = Complex(other.real, other.imag, isOuter=False)
        else:
            return NotImplemented
        return oc - self

    @decorate()
    def __mul__(self, other):
        """复数乘法：(a+bi)(c+di) = (ac-bd)+(ad+bc)i"""
        if not isinstance(other, Complex._complex_type):
            return NotImplemented
        return Complex(
            self.real * other.real - self.imag * other.imag,  # 实部：ac - bd
            self.real * other.imag + self.imag * other.real,  # 虚部：ad + bc
            isOuter=False
        )

    @decorate()
    def __rmul__(self, other):
        """反向乘法：other * self"""
        if isinstance(other, (int, float, Fraction)):
            oc = Complex(other, 0, isOuter=False)
        elif isinstance(other, complex):
            oc = Complex(other.real, other.imag, isOuter=False)
        else:
            return NotImplemented
        return oc * self

    @decorate()
    def __truediv__(self, other):
        """复数除法：(a+bi)/(c+di) = [(ac+bd)+(bc-ad)i]/(c²+d²)"""
        if not isinstance(other, Complex._complex_type):
            return NotImplemented
        self.zero(other)
        return Complex(
            (self.real * other.real + self.imag * other.imag) / (other.real ** 2 + other.imag ** 2),
            (self.imag * other.real - self.real * other.imag) / (other.real ** 2 + other.imag ** 2),
            isOuter=False
        )

    @decorate()
    def __rtruediv__(self, other):
        """反向复数除法：other / self（other为int/float/Fraction/complex）"""
        self.zero(self)
        if isinstance(other, (int, float, Fraction)):
            oc = Complex(other, 0, isOuter=False)
        elif isinstance(other, complex):
            oc = Complex(other.real, other.imag, isOuter=False)
        else:
            return NotImplemented
        return oc / self

    @decorate()
    def __floordiv__(self, other):
        """复数地板除法：先做普通除法，再对实部和虚部分别取地板"""
        if not isinstance(other, Complex._complex_type):
            return NotImplemented
        self.zero(other)
        result = self / other
        if result is NotImplemented:
            return NotImplemented
        f = Complex(0, 0)
        f.real = floor(result.real)
        f.imag = floor(result.imag)
        return Complex(f.real, f.imag, isOuter=False)

    @decorate()
    def __rfloordiv__(self, other):
        """反向复数地板除法：other // self（other为int/float/Fraction/complex）"""
        self.zero(self)
        if isinstance(other, (int, float, Fraction)):
            oc = Complex(other, 0, isOuter=False)
        elif isinstance(other, complex):
            oc = Complex(other.real, other.imag, isOuter=False)
        else:
            return NotImplemented
        return oc // self

    @decorate()
    def __mod__(self, other):
        """实部和虚部分别取余：(a%c) + (b%d)i"""
        if not isinstance(other, Complex._complex_type):
            return NotImplemented
        self.zero(other)
        return Complex(
            self.real % other.real,
            self.imag % other.imag,
            isOuter=False
        )

    @decorate()
    def __rmod__(self, other):
        """反向取余：other的实部%self的实部 + other的虚部%self的虚部"""
        self.zero(self)
        if isinstance(other, (int, float, Fraction)):
            oc = Complex(other, 0, isOuter=False)
        elif isinstance(other, complex):
            oc = Complex(other.real, other.imag, isOuter=False)
        else:
            return NotImplemented
        return oc % self

    @decorate()
    def __pow__(self, other, modulo=None):
        """复数乘幂：支持整数、实数、复数作为指数"""
        # 情况1：指数为整数（优化计算效率）
        if isinstance(other, int):
            return self._pow_integer(other)

        # 情况2：指数为实数或复数（使用指数形式）
        elif isinstance(other, (float, Complex, complex)):
            return self._pow_general(other)

        # 不支持的指数类型
        else:
            return NotImplemented

    @decorate()
    def _pow_integer(self, n: int) -> Complex:
        if n == 0:
            return Complex(1, 0, isOuter=False)
        if n < 0:
            return Complex(1, 0, isOuter=False) / self._pow_integer(-n)

        # 快速幂算法（替代循环）
        result = Complex(1, 0, isOuter=False)  # 初始为乘法单位元
        base = self  # 底数
        while n > 0:
            if n % 2 == 1:  # 若指数为奇数，乘入结果
                result *= base
            base *= base  # 底数平方
            n = n // 2  # 指数减半
        return result

    @decorate()
    def _pow_general(self, exponent) -> Complex:
        """任意指数计算（基于指数形式）"""
        # 1. 计算自身的模长 r 和辐角 theta
        r = abs(self)
        if r == 0:
            return Complex(0, 0, isOuter=False)  # 0的任何正幂为0

        theta = atan2(self.imag, self.real)  # 辐角（弧度）

        # 2. 处理指数（转换为复数以便统一计算）
        if isinstance(exponent, (int, float)):
            exp_real = exponent
            exp_imag = 0.0
        elif isinstance(exponent, Complex):  # 先判断自定义类型
            exp_real = exponent.real
            exp_imag = exponent.imag
        elif isinstance(exponent, complex):  # 再判断内置类型
            exp_real = exponent.real
            exp_imag = exponent.imag
        else:
            return NotImplemented

        # 3. 计算结果的模长和辐角
        new_r = r ** exp_real * exp(-exp_imag * theta)
        new_theta = exp_real * theta + exp_imag * log(r)

        # 4. 转换回代数形式（a + bi）
        real_part = new_r * cos(new_theta)
        imag_part = new_r * sin(new_theta)

        return Complex(real_part, imag_part, isOuter=False)

    @decorate()
    def __rpow__(self, other):
        """反向乘幂：other** self（other为int/float/complex）"""
        # 将other转换为Complex实例（视为实部为other，虚部为0的复数）
        if isinstance(other, (int, float)):
            other = Complex(other, 0, isOuter=False)
        elif isinstance(other, complex):
            other = Complex(other.real, other.imag, isOuter=False)
        else:
            return NotImplemented

        # 复用__pow__：base **self
        return other ** self

    @decorate()
    def __iadd__(self, other: Union[int, float, Fraction, complex, Complex]) -> Complex:
        # 类型转换逻辑
        if isinstance(other, (int, float, Fraction)):
            other = Complex(other, 0, isOuter=False)

        # 使用类级别的类型引用进行检查
        if isinstance(other, Complex._complex_type):
            self.real += other.real
            self.imag += other.imag
        else:
            return NotImplemented
        return self

    @decorate()
    def __isub__(self, other: Union[int, float, Fraction, complex, Complex]) -> Complex:
        # 类型转换逻辑
        if isinstance(other, (int, float, Fraction)):
            other = Complex(other, 0, isOuter=False)

        # 使用类级别的类型引用进行检查
        if isinstance(other, Complex._complex_type):
            self.real -= other.real
            self.imag -= other.imag
        else:
            return NotImplemented
        return self

    @decorate()
    def __imul__(self, other: Union[int, float, Fraction, complex, Complex]) -> Complex:
        if isinstance(other, (int, float, Fraction)):
            other = Complex(other, 0, isOuter=False)
        if isinstance(other, Complex._complex_type):
            result = self * other
            self.real = result.real
            self.imag = result.imag
        else:
            return NotImplemented

        return self

    @decorate()
    def __itruediv__(self, other: Union[int, float, Fraction, complex, Complex]) -> Complex:
        if isinstance(other, (int, float, Fraction)):
            other = Complex(other, 0, isOuter=False)
        if isinstance(other, Complex._complex_type):
            result = self / other
            self.real = result.real
            self.imag = result.imag
        else:
            return NotImplemented

        return self

    @decorate()
    def __ifloordiv__(self, other):
        # 类型转换逻辑
        if isinstance(other, (int, float, Fraction)):
            other = Complex(other, 0, isOuter=False)

        # 使用类级别的类型引用进行检查
        if isinstance(other, Complex._complex_type):
            self.zero(other)
            self /= other
            self.real = floor(self.real)
            self.imag = floor(self.imag)
        else:
            return NotImplemented
        return self

    @decorate()
    def __imod__(self, other):
        # 类型转换逻辑
        if isinstance(other, (int, float, Fraction)):
            other = Complex(other, 0, isOuter=False)

        # 使用类级别的类型引用进行检查
        if isinstance(other, Complex._complex_type):
            self.zero(other)
            self.real = self.real % other.real
            self.imag = self.imag % other.imag
        else:
            return NotImplemented
        return self

    @decorate()
    def __eq__(self, other):
        """复数相等性判断：实部和虚部分别相等"""
        # 处理与非复数类型的比较（如None）
        if not isinstance(other, Complex._complex_type):
            return False
        # 比较实部和虚部（考虑浮点数精度问题，用近似相等）
        return (
                isclose(self.real, other.real, rel_tol=1e-9) and
                isclose(self.imag, other.imag, rel_tol=1e-9)
        )

    def isImaginaryNumber(self) -> bool:
        if self.real == 0 and self.imag != 0:
            return True
        return False
