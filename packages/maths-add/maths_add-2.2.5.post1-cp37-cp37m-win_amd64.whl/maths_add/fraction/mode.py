# encoding:utf-8
from __future__ import annotations
from fractions import Fraction

__all__ = [
    "MathFraction"
]


def ERROR(args, typeList):
    for arg in args:
        is_valid = False
        for t in typeList:
            if isinstance(arg, t):
                is_valid = True
                break
        if not is_valid:
            raise TypeError("The arg must be one of the following types: " + str(typeList) + ".")


class MathFraction(Fraction):
    math_fraction_type = None
    current = Fraction(0)

    def __new__(cls, n, d, isOuter=True):
        # 类型检查
        ERROR([n, d], [int, float])
        if d == 0:
            raise ZeroDivisionError("Denominator cannot be zero")

        # 处理浮点数并化简
        if isinstance(n, float):
            n = Fraction(str(n))
        if isinstance(d, float):
            d = Fraction(str(d))
        frac = Fraction(n, d)

        # 初始化math_fraction_type
        if MathFraction.math_fraction_type is None:
            MathFraction.math_fraction_type = (cls,)
        else:
            MathFraction.math_fraction_type += (cls,)

        # 调用父类的__new__正确初始化实例
        instance = super().__new__(cls, frac.numerator, frac.denominator)
        return instance

    def __init__(self, n, d, isOuter=True):
        self.n = self._numerator  # 复用父类的属性
        self.d = self._denominator

    # 真分数子类：显式继承MathFraction确保布局一致
    class ProperFraction(Fraction):
        def __new__(cls, n, d, isOuter=True):
            # 类型检查
            ERROR([n, d], [int, float])
            if d == 0:
                raise ZeroDivisionError("Denominator cannot be zero")

            # 处理浮点数并化简
            if isinstance(n, float):
                n = Fraction(str(n))
            if isinstance(d, float):
                d = Fraction(str(d))
            frac = Fraction(n, d)

            # 调用父类的__new__正确初始化实例
            instance = super().__new__(cls, frac.numerator, frac.denominator)

            # 真分数核心校验
            if abs(instance._numerator) >= abs(instance._denominator) and isOuter:
                raise ValueError("真分数必须满足：|分子| < |分母|")
            return instance

        def __init__(self, n, d, isOuter=True):
            self.n = self._numerator  # 复用父类的属性
            self.d = self._denominator

    # 假分数子类：显式继承MathFraction确保布局一致
    class ImproperFraction(Fraction):
        def __new__(cls, n, d, isOuter=True):
            # 直接创建ImproperFraction实例，而非转换类型

            # 类型检查
            ERROR([n, d], [int, float])
            if d == 0:
                raise ZeroDivisionError("Denominator cannot be zero")

            # 处理浮点数并化简
            if isinstance(n, float):
                n = Fraction(str(n))
            if isinstance(d, float):
                d = Fraction(str(d))
            frac = Fraction(n, d)

            # 初始化math_fraction_type
            if MathFraction.math_fraction_type is None:
                MathFraction.math_fraction_type = (cls,)
            else:
                MathFraction.math_fraction_type += (cls,)
            # 调用父类的__new__正确初始化实例
            instance = super().__new__(cls, frac.numerator, frac.denominator)
            # 假分数核心校验

            if abs(instance._numerator) < abs(instance._denominator) and isOuter:
                raise ValueError("假分数必须满足：|分子| >= |分母|")

            # 调用父类的__new__正确初始化实例
            instance = super().__new__(cls, frac.numerator, frac.denominator)
            return instance

        def __init__(self, n, d, isOuter=True):
            self.n = self._numerator  # 复用父类的属性
            self.d = self._denominator

    def fraction_class(self):
        # 根据当前值判断是真分数还是假分数
        if abs(MathFraction.current) < 1:
            MathFraction.current = MathFraction.ProperFraction(
                MathFraction.current.numerator,
                MathFraction.current.denominator
            )
        else:
            MathFraction.current = MathFraction.ImproperFraction(
                MathFraction.current.numerator,
                MathFraction.current.denominator
            )


# 测试代码
if __name__ == "__main__":
    # 测试基础实例化
    f = MathFraction(2, 4)  # 化简为1/2
    print(f)  # 输出：1/2

    # 测试真分数
    try:
        proper = MathFraction.ProperFraction(1, 2)
        print(f"真分数: {proper.n}/{proper.d} (类型: {type(proper).__name__})")  # 输出：1/2 (类型: ProperFraction)
    except ValueError as e:
        print(f"真分数错误: {e}")

    # 测试假分数
    try:
        improper = MathFraction.ImproperFraction(3, 2)
        print(type(improper))
        print(f"假分数: {improper.n}/{improper.d} (类型: {type(improper).__name__})")  # 输出：3/2 (类型: ImproperFraction)
    except ValueError as e:
        print(f"假分数错误: {e}")

    # 测试错误案例（真分数传入假分数）
    try:
        MathFraction.ProperFraction(3, 2)
    except ValueError as e:
        print(f"预期错误: {e}")  # 输出：真分数必须满足：|分子| < |分母|
