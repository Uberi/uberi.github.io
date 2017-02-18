#!/usr/bin/env python3

from setuptools import setup

setup(
    name="json_nn",
    version="1.0.0",
    install_requires=["tensorflow>=1.0.0"],
    py_modules=["json_nn"],

    # PyPI metadata
    author="Anthony Zhang (Uberi)",
    author_email="azhang9@gmail.com",
    description="JSON parser, powered by Tensorflow.",
    long_description=open("README.rst").read(),
    license="BSD",
    keywords="json parse parsing tensorflow neural network nn",
    url="http://anthony-zhang.me/blog/json-nn/",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Other OS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ],
)
