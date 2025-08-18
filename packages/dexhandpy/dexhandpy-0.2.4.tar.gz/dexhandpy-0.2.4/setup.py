import os
import sys
import subprocess
import shutil
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.build_ext import build_ext
from os.path import expanduser
home = expanduser("~")
__version__ = "0.2.4"
BASE_DIR = Path(__file__).parent.resolve()
# print(BASE_DIR)
# 自动安装 pybind11
from pybind11.setup_helpers import Pybind11Extension, ParallelCompile, naive_recompile

# Read long description from README
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Fourier dexhand general SDK"

# 启用并行编译
ParallelCompile("NPY_NUM_BUILD_JOBS", needs_recompile=naive_recompile, default=4).install()

# 构建扩展模块
ext_modules = []
source_files = list(map(str, Path(".").glob("*.cpp")))

ext_modules = [
    Pybind11Extension(
        "dexhandpy.fdexhand",
        sources=source_files,
        include_dirs=[
            BASE_DIR / "./fdexhand/include"
        ],
        library_dirs=[
            str(BASE_DIR / "fdexhand/lib"),
            str(BASE_DIR / "../fdexhand/lib")
        ],
        runtime_library_dirs=[
            str(BASE_DIR / "fdexhand/lib"), 
            str(BASE_DIR / "../fdexhand/lib") 
        ],  # 运行时搜索路径
        # libraries=["FourierDexHand"],
        cxx_std=17,
        extra_compile_args=["-fPIC"],
        extra_link_args=[f"-Wl,-rpath,$ORIGIN/../fdexhand/lib",
                         f"-l:libFourierDexHand.so.0"]  
    )
]


setup(
    name='dexhandpy',
    version=__version__,
    author="Afer Liu",
    author_email="fei.liu@fftai.com",
    description="Fourier dexhand general SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/yourusername/dexhandpy",
    
    # 包配置
    packages=find_packages(),
    package_data={
        "fdexhand": ["lib/libFourierDexHand.so.*"],
    },
  
    include_package_data=True,
    
    # 扩展模块
    ext_modules=ext_modules,
    
 
    # 依赖
    setup_requires=["pybind11>=2.6.0"],
    install_requires=["pybind11>=2.6.0"],
    python_requires='>=3.8',
    
    # PyPI 分类
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
)
