#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

# Package meta-data.
NAME = "oafuncs"
DESCRIPTION = "Oceanic and Atmospheric Functions"
URL = "https://github.com/Industry-Pays/OAFuncs"
EMAIL = "liukun0312@stu.ouc.edu.cn"
AUTHOR = "Kun Liu"
REQUIRES_PYTHON = ">=3.10.0"  # 2025/03/13
VERSION = "0.0.98.43"

# What packages are required for this module to be executed?
REQUIRED = [
    # ------ General ------
    "numpy",
    "scipy",
    "pandas",
    "xarray",
    # ------ Progress and Print ------
    "rich",
    # ------ Path ------
    "pathlib",
    # ------ Internet ------
    "lxml",
    "requests",
    "bs4",
    "httpx",
    # ------ Picture ------
    "matplotlib",
    "opencv-python",  # cv2
    # ------ File ------
    "netCDF4",
    "xlrd",
    # ------ Geometry ------
    "geopandas",
    "Cartopy",
    # ------- Data ------
    "rasterio",  # 裁剪数据
    "salem",
    # ------- psutil ------
    "psutil",  # 获取内存信息
    # -------parallel ------
    "dask",  # 并行计算
    # ------- Other ------
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')
        os.system("git branch -m main") 
        os.system("git pull") 
        os.system("git push --force origin main")
        # os.system("git push origin main") # git branch查看是master还是main分支

        sys.exit()


# 确保包含所有包
packages = find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"])
# 显式添加 data_store 目录
# 若添加，还是会被显示为包，但其函数不会被直接显示（应该也可调用）
# 要完全隐藏，但同时包含其py脚本和函数，试试在MANIFEST.in中添加
# 同一级不写__init__.py，但是在MANIFEST.in中写入，就不会显示函数
# if "oafuncs.data_store" not in packages:
#     packages.append("oafuncs.data_store")

# if "oafuncs._nc_script" not in packages:
#     packages.append("oafuncs._nc_script")

# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=packages,  # 使用修改过的包列表
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",  # 确保这里使用的是许可证名称而非文件名
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    # $ setup.py publish support.
    cmdclass={
        "upload": UploadCommand,
    },
)
