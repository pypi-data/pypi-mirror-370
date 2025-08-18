# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='rpa_shopee',  # 包的名字
    version='1.0.2',  # 包的版本
    packages=find_packages(),  # 自动寻找包中的模块
    install_requires=[  # 依赖的其他包
        'selenium==4.27.1'
    ],
    author='Zhongshuizhou',
    author_email='zhongshuizhou@qq.com',
    description='RPA automated execution program for Shopee',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://www.jeoshi.com',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',  # 支持的Python版本
)
