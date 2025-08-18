#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# @Time    : 2025/8/6 下午3:29
# @Author  : 单子叶蚕豆_DzyCd
# @File    : setup.py
# @IDE     : PyCharm
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot_plugin_imagelibrary",
    version="1.1.0",
    author="ISOM_DzyCd",
    author_email="dzycd53@gmail.com",
    description="Create a shared Image Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    urls={"Repository": "https://github.com/DZYCD/nonebot-plugin-ImageLibrary"},
    packages=["nonebot_plugin_ImageLibrary"],
    install_requires=["nonebot2>=2.4.0,<3.0.0", "nonebot-adapter-onebot >=2.2.0", "nonebot-plugin-localstore>=0.7.4,<1.0.0", "aiohttp >=3.0.0"],
    entry_points={
        'console_scripts': [
            'ImageLibrary=ImageLibrary:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
