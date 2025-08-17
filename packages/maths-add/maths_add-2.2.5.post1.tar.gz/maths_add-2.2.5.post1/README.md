# maths_add

## 一个数学扩展库

Python要求：版本≥3.7.0

## 安装方法（重点！！！）
1. 在cmd中使用`pip install maths_add`下载安装
2. 在PYPI网站中下载：
   - 可下载.whl文件，在下载目录的cmd中输入`pip install 文件名.whl`安装
   - 可下载压缩包，解压后在当前目录的cmd中输入`python setup.py install`安装

## 项目分支
1. **基础计算模块**
   - 包含加法、减法等基本运算，通过封装的函数提供便捷调用接口，支持多参数传入计算。

2. **高级计算模块**
   - 提供对数、幂运算等高级数学计算功能，满足复杂数学运算需求。

3. **复数运算模块**
   - 实现自定义复数类`Complex`，支持复数的加减乘除、幂运算、模长计算等操作，兼容与整数、浮点数等类型的交互。

4. **分数运算模块**
   - 定义`Mixed`类处理带分数运算，支持与整数、浮点数、分数的各种算术运算，包括加减乘除、取模、幂运算等。

5. **几何计算模块**
   - 涵盖三维图形（如立方体）的棱长和等几何参数计算，提供简洁的函数接口。

6. **算法实现模块**
   - 通过C++扩展实现快速幂、冒泡排序、插入排序、选择排序、归并排序等算法，并封装为Python可调用的接口，提升计算效率。

7. **加密解密模块**
   - 包含RSA、SHA-256、AES等加密相关功能，提供密钥处理、数据加密解密等操作函数。

8. **特殊数字处理模块**
   - 提供归并排序等针对特殊数字或序列的处理函数。

## 异常处理
- 内置`decorate`装饰器，为各类函数提供统一的异常处理机制，支持日志记录、异常抑制、返回默认值等功能，增强代码的健壮性。

## 使用示例
```python
# 复数运算示例
from maths_add.complex.comp import Complex
c1 = Complex(1, 1)
c2 = Complex(1, 1)
print(c1 + c2)  # 输出：2+2i

# 分数运算示例
from maths_add.fraction.code import Mixed
from fractions import Fraction
from maths_add.fraction.mode import MathFraction
m1 = Mixed(0, Fraction(3, 4))
m2 = Mixed(0, Fraction(1, 2))
print(m1 * m2)  # 输出：w=0, f=3/8
f1 = MathFraction(0, 2).fraction_class()
print(type(f1)) # 输出：<class 'maths_add.fraction.mode.MathFraction'>
f2 = MathFraction.ImproperFraction(1, 2) # 报错：ValueError:假分数必须满足：|分子| > |分母|
```