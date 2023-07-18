#!/usr/bin/env python

from setuptools import setup

with open("README.md", "rt") as fh:
    long_description = fh.read()

dependencies = [
    "blspy>=0.9",
]

dev_dependencies = [
    "klvm_tools>=0.4.4",
    "pytest",
]

setup(
    name="klvm",
    packages=["klvm",],
    author="Chik Network, Inc.",
    author_email="hello@chiknetwork.com",
    url="https://github.com/Chik-Network/klvm",
    license="https://opensource.org/licenses/Apache-2.0",
    description="[Contract Language | Chiklisp] Virtual Machine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=dependencies,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Security :: Cryptography",
    ],
    extras_require=dict(dev=dev_dependencies,),
    project_urls={
        "Bug Reports": "https://github.com/Chik-Network/klvm",
        "Source": "https://github.com/Chik-Network/klvm",
    },
)
