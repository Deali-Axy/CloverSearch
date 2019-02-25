from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '0.1.19'
description = 'CloverSearch搜索引擎的Django模块，使用起来超级方便！'
update = '优化建立索引、搜索性能，测试性能提高10倍以上，但是受限于Python语言的性能，数据量大的时候性能还是不够理想，有待进一步优化。'
description = '{}。版本[{}]更新内容：{}'.format(description, version, update)

setup(
    name='cloversearch',
    version=version,
    packages=setuptools.find_packages(),
    install_requires=[
        'jieba>=0.39',
        'django',
        'ujson'
    ],
    url='https://github.com/Deali-Axy',
    # license='GPLv3',
    author='DealiAxy',
    author_email='dealiaxy@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
