import os
import sys
from pathlib import Path
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
import pybind11

# 读取版本信息
def get_version():
    version_file = Path(__file__).parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "3.6"

# 读取README
def get_long_description():
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        return readme_file.read_text(encoding='utf-8')
    return "Encrypted ODOO module"

# 编译器特定设置
def get_compile_args():
    """根据编译器返回合适的编译参数"""
    if sys.platform.startswith('win'):
        # Windows MSVC
        return [
            '/utf-8',      # 指定源文件编码为UTF-8
            '/wd4819',     # 禁用编码警告C4819
            '/O2',         # 优化
        ]
    else:
        # GCC/Clang
        return [
            '-O3',                    # 优化
            '-finput-charset=utf-8',  # 指定输入编码
            '-fexec-charset=utf-8',   # 指定执行编码
            '-fvisibility=hidden',    # 隐藏符号
        ]

def get_link_args():
    """根据平台返回合适的链接参数"""
    if sys.platform.startswith('win'):
        return []
    elif sys.platform.startswith('darwin'):
        # macOS
        return ['-undefined', 'dynamic_lookup']
    else:
        # Linux
        return ['-Wl,--strip-all']

# 扩展模块配置
ext_modules = [
    Pybind11Extension(
        "fast_demo",
        [
            "src/main.cpp",
        ],
        include_dirs=[
            pybind11.get_include(),
        ],
        language='c++',
        cxx_std=14,
        define_macros=[
            ('VERSION_INFO', f'"{get_version()}"'),
            ('UNICODE', None),
            ('_UNICODE', None),
        ] if sys.platform.startswith('win') else [
            ('VERSION_INFO', f'"{get_version()}"'),
        ],
        extra_compile_args=get_compile_args(),
        extra_link_args=get_link_args(),
    ),
]

setup(
    name="fast-demo",
    version=get_version(),
    author="RoyZhou",
    author_email="2820003660@qq.com",
    url="https://github.com/your-username/fast-demo",
    description="Encrypted ODOO module",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "pybind11>=2.6.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/fast-demo/issues",
        "Source": "https://github.com/your-username/fast-demo",
    },
)
