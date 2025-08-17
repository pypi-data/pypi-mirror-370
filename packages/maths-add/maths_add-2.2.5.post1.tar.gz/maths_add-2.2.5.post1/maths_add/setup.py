from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys


# 自定义 build_ext 命令，强制使用 g++ 作为编译器
class BuildExt(build_ext):
    def build_extensions(self):
        # 指定编译器为 g++
        if sys.platform == 'win32':
            self.compiler.compiler_so = ['g++']  # Windows 上使用 g++
            self.compiler.linker_so = ['g++', '-shared']

        build_ext.build_extensions(self)


# 定义扩展模块
module = Extension(
    'example',  # 模块名称
    sources=['example.cpp']  # 源代码文件
)

# 设置模块
setup(
    name='example',
    version='1.0',
    description='Example module written in C++',
    ext_modules=[module]
)
