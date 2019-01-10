from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '0.1.15'
description = 'CloverSearch搜索引擎的Django模块，使用起来超级方便！'
update = '总算把CloverSearch的核心功能提取成Django模块，终于可以用了！'
description = '{}。版本[{}]更新内容：{}'.format(description, version, update)

setup(
    name='cloversearch',
    version=version,
    packages=setuptools.find_packages(),
    install_requires=[
        'jieba>=0.39',
        'django',
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
