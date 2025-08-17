from setuptools import setup, find_packages, Extension
import distutils.cygwinccompiler
import os


# 强制使用 MinGW-w64
def patch_msvc_version():
    original_get_msvcr = distutils.cygwinccompiler.get_msvcr

    def patched_get_msvcr():
        try:
            return original_get_msvcr()
        except ValueError:
            # 返回 MinGW 的运行时库
            return ['msvcrt']

    distutils.cygwinccompiler.get_msvcr = patched_get_msvcr


# 应用补丁
patch_msvc_version()

# 定义 C++ 扩展模块
maths_add_module = Extension(
    'maths_add.example',  # 模块的完整名称，可按需调整
    sources=['maths_add/example.cpp'],  # C++ 源文件的路径，需替换为实际路径
    language='c++',  # 指定使用 C++ 编译
    # extra_compile_args=['/utf-8']  # 关键：添加UTF-8支持
)

setup(
    name='maths_add',
    version='2.2.5.post1',
    description='A extended math library',
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='fourth-dimensional_universe',
    author_email='3817201131@qq.com',
    url='https://github.com/fourth-dimensional/maths_add',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'pycryptodome',
        'cryptography',
        'sympy'
    ],
    ext_modules=[maths_add_module]  # 添加扩展模块到打包配置
)
