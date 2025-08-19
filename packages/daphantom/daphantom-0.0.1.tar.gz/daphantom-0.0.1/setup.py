# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
def readmeS():
    if os.path.exists("README.md"):
        return open("README.md", encoding="utf-8").read()
    return "No description available."

setup(
    name='daphantom',  # 包的名字
    version='0.0.1',  # 包的版本
    packages=find_packages(),  # 自动寻找包中的模块
    install_requires=[  # 依赖的其他包
        # 'selenium==4.27.1'
    ],
    author='Xiaomu',
    author_email='jiangongfang@foxmail.com',
    description="Ghost Crawler Data Terminator - a stealthy web crawler framework by Xiaomu (小木).",
    long_description=readmeS(),
    long_description_content_type='text/markdown',
    url='https://www.jiangongfang.top',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license="MIT",
    python_requires='>=3.8',  # 支持的Python版本
)
