#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("version.json","r", encoding="utf-8") as vf:
    v = json.load(vf)
    version = v["version"]

setuptools.setup(
    name="BusMessageParser",  # 包名
    version=version,
    author="Abyss",
    author_email="",
    description="总线报文记录文件检测",  # 包的简述
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    packages=setuptools.find_packages(),
)


