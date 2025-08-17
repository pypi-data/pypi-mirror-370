# encoding:utf-8
from __future__ import annotations
import warnings
from fractions import Fraction
from typing import Union
from maths_add import factors_and_multiples_numbers, special_numbers
from maths_add.except_error import decorate

__all__ = [
    "Mixed",
    "Hf",
    "get_f",
    "find_a_common_denominator",
    "improper_to_mixed",
    "mixed_to_improper"
]


class PFWarnings(UserWarning):
    pass


def ERROR(args, typeList):
    for arg in args:
        is_valid = False
        for t in typeList:
            if isinstance(arg, t):
                is_valid = True
                break
        if not is_valid:
            raise TypeError("The arg must be one of the following types: " + str(typeList) + ".")


class Mixed(object):
    # 类级别变量保存自身类型引用
    _mixed_type = None

    @decorate()
    def __init__(self, w, f, isOuter=True):
        ERROR([w], [int])
        ERROR([f], [Fraction])
        if abs(f) >= 1:
            if isOuter:
                warnings.warn("The f must be a proper fraction.", PFWarnings)
            integer_part = f.numerator // f.denominator
            w += integer_part
            f -= integer_part

        # 处理符号不一致的情况
        if w > 0 > f or w < 0 < f:
            total = Fraction(w) + f
            w = total.numerator // total.denominator
            f = total - w

        self.w = w
        self.f = f
        self.i = isOuter  # 用于控制__del__输出

        # 初始化类类型引用
        if Mixed._mixed_type is None:
            Mixed._mixed_type = self.__class__

    @decorate()
    def zero(self, n: Union[int, float, Fraction, Mixed]) -> None:
        """检查是否为零，支持Mixed类型"""
        if isinstance(n, Mixed):
            n = n._to_fraction()
        if n == 0:
            raise ZeroDivisionError("除数不能为零")

    @decorate()
    def _to_fraction(self) -> Fraction:
        """转换为假分数"""
        return Fraction(
            self.w * self.f.denominator + self.f.numerator,
            self.f.denominator
        )

    @decorate()
    def __del__(self):
        if self.i:  # 仅外部创建的实例输出销毁信息
            print("对象被销毁")

    @decorate()
    def __str__(self) -> str:
        return f"w={self.w}, f={self.f}"

    @decorate()
    def __repr__(self) -> str:
        return f"Mixed(w={self.w}, f={self.f})"

    @decorate()
    def __pos__(self) -> Mixed:
        return Mixed(+self.w, +self.f)

    @decorate()
    def __neg__(self) -> Mixed:
        return Mixed(-self.w, -self.f)

    @decorate()
    def __abs__(self) -> Mixed:
        return Mixed(abs(self.w), abs(self.f))

    @decorate()
    def __add__(self, other: Mixed) -> Mixed:
        ERROR([other], [Mixed])
        new_w = self.w + other.w
        new_f = self.f + other.f
        return Mixed(new_w, new_f, isOuter=False)

    @decorate()
    def __radd__(self, other: Union[int, float, Fraction]) -> Mixed:
        ERROR([other], [int, float, Fraction])
        tm = Mixed(0, Fraction(str(other)), isOuter=False)
        return self + tm

    @decorate()
    def __sub__(self, other: Mixed) -> Mixed:
        ERROR([other], [Mixed])
        new_w = self.w - other.w
        new_f = self.f - other.f
        return Mixed(new_w, new_f, isOuter=False)

    @decorate()
    def __rsub__(self, other: Union[int, float, Fraction]) -> Mixed:
        ERROR([other], [int, float, Fraction])
        tm = Mixed(0, Fraction(str(other)), isOuter=False)
        return tm - self

    @decorate()
    def __mul__(self, other: Mixed) -> Mixed:
        ERROR([other], [Mixed])
        sf = self._to_fraction()
        of = other._to_fraction()
        nf = sf * of
        return Mixed(nf.numerator // nf.denominator, nf - (nf.numerator // nf.denominator), isOuter=False)

    @decorate()
    def __rmul__(self, other: Union[int, float, Fraction]) -> Mixed:
        ERROR([other], [int, float, Fraction])
        tm = Mixed(0, Fraction(str(other)), isOuter=False)
        return self * tm

    @decorate()
    def __truediv__(self, other: Mixed) -> Mixed:
        ERROR([other], [Mixed])
        sf = self._to_fraction()
        of = other._to_fraction()
        self.zero(of)
        nf = sf / of
        return Mixed(nf.numerator // nf.denominator, nf - (nf.numerator // nf.denominator), isOuter=False)

    @decorate()
    def __rtruediv__(self, other: Union[int, float, Fraction]) -> Mixed:
        ERROR([other], [int, float, Fraction])
        tm = Mixed(0, Fraction(str(other)), isOuter=False)
        self.zero(self)
        return tm / self

    @decorate()
    def __floordiv__(self, other: Mixed) -> Mixed:
        ERROR([other], [Mixed])
        sf = self._to_fraction()
        of = other._to_fraction()
        self.zero(of)
        nf = sf // of
        return Mixed(nf.numerator // nf.denominator, Fraction(0), isOuter=False)

    @decorate()
    def __rfloordiv__(self, other: Union[int, float, Fraction]) -> Mixed:
        ERROR([other], [int, float, Fraction])
        tm = Mixed(0, Fraction(str(other)), isOuter=False)
        self.zero(self)
        return tm // self

    @decorate()
    def __mod__(self, other: Mixed) -> Mixed:
        ERROR([other], [Mixed])
        sf = self._to_fraction()
        of = other._to_fraction()
        self.zero(of)
        nf = sf % of
        return Mixed(0, nf, isOuter=False)

    @decorate()
    def __rmod__(self, other: Union[int, float, Fraction]) -> Mixed:
        ERROR([other], [int, float, Fraction])
        tm = Mixed(0, Fraction(str(other)), isOuter=False)
        self.zero(self)
        return tm % self

    @decorate()
    def __pow__(self, other: Mixed) -> Mixed:
        ERROR([other], [Mixed])
        sf = self._to_fraction()
        of = other._to_fraction()
        try:
            nf = Fraction(sf ** of)
        except ValueError:
            return NotImplemented  # 无理数结果不支持
        return Mixed(nf.numerator // nf.denominator, nf - (nf.numerator // nf.denominator), isOuter=False)

    @decorate()
    def __rpow__(self, other: Union[int, float, Fraction]) -> Mixed:
        ERROR([other], [int, float, Fraction])
        tm = Mixed(0, Fraction(str(other)), isOuter=False)
        return tm ** self

    @decorate()
    def __iadd__(self, other: Union[int, float, Fraction, Mixed]) -> Mixed:
        # 类型转换逻辑
        if isinstance(other, float):
            other = Fraction(str(other))
        elif isinstance(other, Fraction):
            other = Mixed(other.numerator // other.denominator,
                          other - (other.numerator // other.denominator),
                          isOuter=False)
        elif isinstance(other, int):
            other = Mixed(other, Fraction(0), isOuter=False)

        # 使用类级别的类型引用进行检查
        if isinstance(other, Mixed._mixed_type):
            self.w += other.w
            self.f += other.f
        else:
            return NotImplemented
        return self

    @decorate()
    def __isub__(self, other: Union[int, float, Fraction, Mixed]) -> Mixed:
        if isinstance(other, float):
            other = Fraction(str(other))
        elif isinstance(other, Fraction):
            other = Mixed(other.numerator // other.denominator,
                          other - (other.numerator // other.denominator),
                          isOuter=False)
        elif isinstance(other, int):
            other = Mixed(other, Fraction(0), isOuter=False)

        if isinstance(other, Mixed._mixed_type):
            self.w -= other.w
            self.f -= other.f
        else:
            return NotImplemented

        return self

    @decorate()
    def __imul__(self, other: Union[int, float, Fraction, Mixed]) -> Mixed:
        if isinstance(other, float):
            other = Fraction(str(other))
        elif isinstance(other, Mixed._mixed_type):
            # 转换Mixed为Fraction
            fz = other.w * other.f.denominator + other.f.numerator
            fm = other.f.denominator
            other = Fraction(fz, fm)
        elif isinstance(other, int):
            other = Fraction(other)
        else:
            return NotImplemented

        sf = self._to_fraction() * other
        self.w = sf.numerator // sf.denominator
        self.f = sf - self.w
        return self

    @decorate()
    def __itruediv__(self, other: Union[int, float, Fraction, Mixed]) -> Mixed:
        if isinstance(other, float):
            other = Fraction(str(other))
        elif isinstance(other, Mixed._mixed_type):
            fz = other.w * other.f.denominator + other.f.numerator
            fm = other.f.denominator
            other = Fraction(fz, fm)
        elif isinstance(other, int):
            other = Fraction(other)
        else:
            return NotImplemented

        self.zero(other)
        sf = self._to_fraction() / other
        self.w = sf.numerator // sf.denominator
        self.f = sf - self.w
        return self

    @decorate()
    def __ifloordiv__(self, other: Union[int, float, Fraction, Mixed]) -> Mixed:
        if isinstance(other, float):
            other = Fraction(str(other))
        elif isinstance(other, Mixed._mixed_type):
            fz = other.w * other.f.denominator + other.f.numerator
            fm = other.f.denominator
            other = Fraction(fz, fm)
        elif isinstance(other, int):
            other = Fraction(other)
        else:
            return NotImplemented

        self.zero(other)
        sf = self._to_fraction() // other
        self.w = sf.numerator // sf.denominator
        self.f = sf - self.w
        return self

    @decorate()
    def __imod__(self, other: Union[int, float, Fraction, Mixed]) -> Mixed:
        if isinstance(other, float):
            other = Fraction(str(other))
        elif isinstance(other, Mixed._mixed_type):
            fz = other.w * other.f.denominator + other.f.numerator
            fm = other.f.denominator
            other = Fraction(fz, fm)
        elif isinstance(other, int):
            other = Fraction(other)
        else:
            return NotImplemented

        self.zero(other)
        sf = self._to_fraction() % other
        self.w = 0
        self.f = sf
        return self

    @decorate()
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mixed._mixed_type):
            return NotImplemented
        return self.w == other.w and self.f == other.f

    @decorate()
    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Mixed._mixed_type):
            return NotImplemented
        return not self.__eq__(other)

    @decorate()
    def __lt__(self, other: Mixed) -> bool:
        if not isinstance(other, Mixed._mixed_type):
            return NotImplemented
        return self._to_fraction() < other._to_fraction()

    @decorate()
    def __gt__(self, other: Mixed) -> bool:
        if not isinstance(other, Mixed._mixed_type):
            return NotImplemented
        return self._to_fraction() > other._to_fraction()

    @decorate()
    def get_m(self) -> str:
        """返回带分数的字符串表示（如 "2 1/3"）"""
        return f"{self.w} {self.f}" if self.w != 0 else str(self.f)

    @decorate()
    def mixed_to_improper(self) -> Fraction:
        """转换为假分数"""
        return self._to_fraction()


def __init__(self):
    pass


@decorate()
def fzx(self, f):
    ERROR([f], [Fraction])
    x = f.numerator / f.denominator
    return x


@decorate()
def xfz(self, x):
    ERROR([x], [float])
    f = Fraction(x)
    return f


Hf = type("Hf", (), {"__init__": __init__, "fzx": fzx, "xfz": xfz})


@decorate()
def get_f(a, b):
    ERROR((a, b), [int, float, Fraction])
    if type(a) == float or type(b) == float:
        al = special_numbers.获取小数点后的位数(a)
        bl = special_numbers.获取小数点后的位数(b)
        nl = max(al, bl)
        a *= pow(10, nl)
        b *= pow(10, nl)
    f = Fraction(a, b)
    return f, (f.numerator, f.denominator)


@decorate()
def find_a_common_denominator(a, b):
    ERROR((a, b), [Fraction])
    c = factors_and_multiples_numbers.the_Smallest_Same_multiples(a.denominator, b.denominator)
    aList = {"numerator": a.numerator * c / a.denominator, "denominator": c}
    bList = {"numerator": b.numerator * c / b.denominator, "denominator": c}
    return aList, bList


@decorate()
def improper_to_mixed(f):
    ERROR([f], [Fraction])
    # 计算整数部分
    whole_part = f.numerator // f.denominator
    # 计算分数部分
    remaining_fraction = f - whole_part
    if remaining_fraction == 0:
        return str(whole_part)
    elif whole_part == 0:
        return str(f)
    else:
        return str(whole_part) + str(remaining_fraction)


@decorate()
def mixed_to_improper(whole, f):
    ERROR([whole], [int])
    ERROR([f], [Fraction])
    numerator = f.numerator
    numerator += whole * f.denominator
    fn = Fraction(numerator, f.denominator)
    return fn

