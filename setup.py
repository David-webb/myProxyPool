#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Tengwei'

import ez_setup
ez_setup.use_setuptools()   # 这两行是当setuptools不存在时,自动从网上下载安装所需的setuptools包.
from setuptools import setup, find_packages
setup(
    name="myProxyPool",
    version="0.1",
    packages=find_packages(),     # 常用,要熟悉 :会自动查找当前目录下的所有模块(.py文件) 和包(包含__init___.py文件的文件夹)
    scripts=['UsefulProxyPool.py', 'xiciDbOps.py', 'xiciSetup.py'],
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['docutils>=0.3'],       # 常用
    # entry_points={
    #     'console_scripts': [
    #         'foo = demo:test',
    #         'bar = demo:test',
    #     ],
    #     'gui_scripts': [
    #         'baz = demo:test',
    #     ]
    # },
    # metadata for upload to PyPI
    author="Tengwei",
    author_email="471435549@qq.com",
    description="this is a proxypool for wlw club",
    # license="PSF",
    keywords="wlw proxypools",
    # url="http://example.com/HelloWorld/",   # project home page, if any
    # could also include long_description, download_url, classifiers, etc.
)