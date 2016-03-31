from setuptools import setup, find_packages
import os
from osuapi import __version__ as version, __title__ as name, __author__ as author, __license__ as license


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name=name,
    version=version,
    author=author,
    license="MIT",
    keywords="osu",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
      "Development Status :: 1 - Planning",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Topic :: Utilities"
    ]
)