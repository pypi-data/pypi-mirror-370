import distutils.cygwinccompiler
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys


# 修复 MSVC 版本检测
def patch_get_msvcr():
    original_get_msvcr = distutils.cygwinccompiler.get_msvcr

    def patched_get_msvcr():
        try:
            return original_get_msvcr()
        except ValueError:
            return ['msvcrt']  # 使用 MinGW 的运行时库

    distutils.cygwinccompiler.get_msvcr = patched_get_msvcr


# 应用补丁
patch_get_msvcr()


# 自定义 build_ext 命令，强制使用 g++
class CustomBuildExt(build_ext):
    def build_extensions(self):
        # 强制使用 g++ 作为编译器
        if sys.platform == 'win32':
            self.compiler.compiler_so = ['g++']  # 编译器
            self.compiler.linker_so = ['g++', '-shared']  # 链接器

        # 移除 msvcr140 依赖
        for ext in self.extensions:
            if hasattr(ext, 'libraries') and 'msvcr140' in ext.libraries:
                ext.libraries.remove('msvcr140')
                if 'msvcrt' not in ext.libraries:
                    ext.libraries.append('msvcrt')

        build_ext.build_extensions(self)


# 定义扩展模块（确保文件扩展名为 .cpp）
module = Extension(
    'example',
    sources=['example.cpp'],  # 改为 .cpp 扩展名
    language='c++',  # 显式指定 C++ 语言
)

# 设置模块
setup(
    name='example',
    version='1.0',
    ext_modules=[module],
    cmdclass={'build_ext': CustomBuildExt},  # 使用自定义命令
)